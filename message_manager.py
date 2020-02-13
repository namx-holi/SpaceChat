
import json
import queue
import select
import socket
import struct
import threading


class Message:
	def __init__(self, user, msg):
		self.user = user
		self.msg = msg
	@property
	def content(self):
		return f"{self.user}: {user.msg}"
	def encode(self):
		content = json.dumps(dict(
			user=self.user,
			msg=self.msg))
		return to_packet(content)
	def __repr__(self):
		return f"<Message {self.user}:`{self.msg}`>"


class ServerMessage(Message):
	def __init__(self, msg):
		super().__init__("SERVER", msg)
	def __repr__(self):
		return f"<ServerMessage `{self.msg}`>"


def to_packet(content):
	content_bytes = content.encode()
	msg_len_bytes = struct.pack("I", len(content_bytes))
	return msg_len_bytes + content_bytes


# I want users to be able to make a socket connection to the server.
# They then send their API token.

# If they get a response saying "OK", then all good!
# If they get a response saying "FAILED: msg", then bad!!!

# When a connection is successful, I want to start sending broadcast
# messages to that connection!



host = "0.0.0.0"
port = 7778
timeout = 0.25


class MessageManager:

	def __init__(self, sessions):
		self.sessions = sessions
		self.conn_message_queues = set()
		self.conn_to_queue_map = dict()


	# Start this as a thread (nonblocking)
	def start(self, port):
		# Wrapps start with threading
		running_thread = threading.Thread(
			target=self.run,
			args=[port])
		# running_thread.daemon = True
		running_thread.start()


	# Start this as a main process (not much use honestly)
	def run(self, port):
		host = "0.0.0.0"

		# Set up socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((host, port))

		# Start listening and handle connections
		server.listen(20)
		print(f" [*] Starting MessageManager on port {port}")
		self.listen_loop(server)

		# Once done, close socket
		# server.shutdown(socket.SHUT_RDWR)
		server.close()


	# Waits for connections. On connection, push to client_handler
	def listen_loop(self, server):
		# Listen for connections
		# On connection, start thread. Add conn to this.
		while True:
			conn, addr = server.accept()
			client_handler_thread = threading.Thread(
				target=self.client_handler,
				args=[conn, addr])
			client_handler_thread.start()


	# Handles one connection
	def client_handler(self, conn, addr):
		print("Accepted {}:{}".format(*addr))

		# Check given token
		success, msg = self.auth_conn(conn)
		if not success:
			print("{}:{} failed authentication on broadcast server".format(*addr))
			conn.send(to_packet(json.dumps(msg)))
			conn.close()
			return

		print("{}:{} Authenticated!".format(*addr))
		conn.send(to_packet(json.dumps(msg)))

		# Register this connection with manager.
		# When registered with manager, any message added
		# to be sent, it's added to a queue associated with
		# each connected client, which can then be popped!
		q = self.register_conn(conn)

		# Turn off blocking so we can read with timeout
		conn.setblocking(0)

		while True:

			# Check if a message to send (with small timeout)
			try:
				msg = q.get(timeout=timeout)
			except queue.Empty:
				# No message to send to the client!
				pass
			else:
				# Send the msg to the client
				conn.send(msg.encode())


			# Try receive anything (could be an exit)
			ready = select.select([conn], [], [], timeout)
			if ready[0]:
				raw = conn.recv(1024)
				data = raw.decode().strip()
				if data.upper() == "EXIT":
					# If exit, stop this!
					break

		self.unregister_conn(conn)
		conn.close()
		print("Connection to {}:{} closed.".format(*addr))


	def auth_conn(self, conn):
		print(self.sessions)

		token_raw = conn.recv(36)
		token = token_raw.decode()

		if token not in self.sessions:
			return False, dict(error="invalid token")

		return True, dict(msg="logged in to broadcast server")


	def register_conn(self, conn):
		q = queue.Queue()
		self.conn_message_queues.add(q)
		self.conn_to_queue_map[conn] = q
		return q


	def unregister_conn(self, conn):
		q = self.conn_to_queue_map[conn]
		q.queue.clear() # Not necessary
		self.conn_message_queues.remove(q)
		del self.conn_to_queue_map[conn]


	def send_to_all(self, msg, user="SERVER"):
		if not isinstance(msg, Message):
			# We create an instance here 
			# use pointers to the instance to save mem
			msg = Message(user, msg)

		for q in self.conn_message_queues:
			q.put(msg)
