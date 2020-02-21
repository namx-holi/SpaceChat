
import json
import queue
import select
import socket
import struct
import threading


MSG_LEN_CHAR = "I" # Represents an int
MSG_LEN_BYTES = struct.calcsize(MSG_LEN_CHAR)

HOST = "0.0.0.0"
PORT = 7778

MSG_CHECK_TIMEOUT = 0.25 # Seconds



class Message:
	@property
	def content(self):
		return dict(
			msg=self.msg)
	def __init__(self, msg):
		self.msg = msg
	def encode(self):
		data = json.dumps(self.content)
		return to_packet(data)
	def __repr__(self):
		return f"<Message '{self.msg}'>"


class UserMessage(Message):
	@property
	def content(self):
		return dict(
			username=self.user.username,
			msg=self.msg)
	def __init__(self, user, msg):
		super().__init__(msg)
		self.user = user
	def __repr__(self):
		return f"<UserMessage '{self.user.name}: {self.msg}'>"


class WhisperMessage(Message):
	@property
	def content(self):
		return dict(
			username=self.user.username,
			recipient=self.recipient.username,
			msg=self.msg)
	def __init__(self, user, recipient, msg):
		super().__init__(msg)
		self.user = user
		self.recipient = recipient
	def __repr__(self):
		return "<WhisperMessage to {}: '{}: {}'>".format(
			self.recipient.name, self.user.name, self.msg)


class ServerMessage(Message):
	def __init__(self, msg):
		super().__init__(msg)
	def __repr__(self):
		return f"<ServerMessage '{self.msg}'>"



def to_packet(content):
	content_bytes = content.encode()
	msg_len_bytes = struct.pack(MSG_LEN_CHAR, len(content_bytes))
	return msg_len_bytes + content_bytes


"""
TODO: A class that manages all the connections.

It will have a socket that players can connect to.

The socket will require you to send your token to
log in.

This token can be sent multiple times to refresh the
session. Before sending messages, the token of the
player is checked and compared. If the login token is
invalid, the player will get an error message saying so.

When the token of the player is changed or the player
is logged out, the player will also recv a message
from this socket saying so.

As long as the token is valid, the player will recv
messages from their terrain, as well as the server.
"""
class MessageManager:

	def __init__(self, session_manager, **kwargs):
		self.session_manager = session_manager
		self.conn_limit = kwargs.get("conn_limit", 20)

		# Used to look up the connection from a user
		self.user_to_queue_map = dict()
		self.client_queues = set()

		running_thread = threading.Thread(
			target=self.run)
		running_thread.start()


	def run(self):
		# Set up socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((HOST, PORT))

		# Start listening and handle connections
		server.listen(self.conn_limit)
		print(f" [*] Starting MessageManager on port {PORT}")
		self.listen_loop(server)

		# Once done, close socket
		server.close()


	def listen_loop(self, server):
		while True:
			conn, addr = server.accept()
			client_handler_thread = threading.Thread(
				target=self.client_handler,
				args=[conn, addr])
			client_handler_thread.start()


	def client_handler(self, conn, addr):
		print("Accepted connection from {}:{}".format(*addr))

		# Check given token
		session = self.auth_conn(conn)
		if not session:
			print("{}:{} failed authentication.".format(*addr))
			conn.close()
			return
		print("{}:{} authenticated!".format(*addr))

		# Register this connection with manager.
		q = self.register_client(session.user)

		# Turn off blocking so we can read with timeout
		conn.setblocking(0)

		while True:
			# Check if a message to send
			try:
				msg = q.get(timeout=MSG_CHECK_TIMEOUT)
			except queue.Empty:
				# No message to send to the client!
				pass
			else:
				self._send(conn, session.user, msg)

			# Try receive anything (could be an exit)
			ready = select.select([conn], [], [], MSG_CHECK_TIMEOUT)
			if ready[0]:
				raw = conn.recv(1024)

				# If we were sent nothing but the socket was ready,
				# the client disconnected.
				if not raw:
					break

				data = raw.decode().strip()
				if data.upper() == "EXIT":
					# If exit, stop this!
					break

		self.unregister_client(session.user)
		conn.close()
		print("Connection to {}:{} closed.".format(*addr))


	def _send(self, conn, user, msg):
		if isinstance(msg, ServerMessage):
			# Server messages are broadcasts
			conn.send(msg.encode())

		elif isinstance(msg, UserMessage):
			# User messages are for same terrain only
			if msg.user.rover.terrain == user.rover.terrain:
				conn.send(msg.encode())

		elif isinstance(msg, WhisperMessage):
			# Whispers are only for those who sent it
			# and the person it's directed at
			if msg.user == user or msg.recipient == user:
				conn.send(msg.encode())

		else:
			# Not sure what this is! Send it anyway!
			print("Unknown message type:", msg)
			conn.send(msg.encode())


	def auth_conn(self, conn):
		token_raw = conn.recv(36)
		token = token_raw.decode()
		session = self.session_manager.get_by_token(token)

		if not session:
			msg = dict(error="invalid token")
			conn.send(to_packet(json.dumps(msg)))
			return

		msg = dict(msg="logged into to broadcast server")
		conn.send(to_packet(json.dumps(msg)))
		return session


	def register_client(self, user):
		q = queue.Queue()

		# Check if this user is already registered.
		if user in self.user_to_queue_map:
			self.unregister_client(user)

		self.user_to_queue_map[user] = q
		self.client_queues.add(q)
		return q


	def unregister_client(self, user):
		q = self.user_to_queue_map[user]
		q.queue.clear() # Not necessary
		self.client_queues.remove(q)
		del self.user_to_queue_map[user]


	def send_message(self, user, msg):
		msg = UserMessage(user, msg)

		# TODO: Think of getting the terrain of the
		# user with user.rover.terrain, then adding
		# only to the queues of users on that
		# terrain. Would lessen the overhead for
		# each user session process!

		for q in self.client_queues:
			q.put(msg)


	def send_whisper(self, user, recipient, msg):
		msg = WhisperMessage(user, recipient, msg)

		# Just put in the user and recipient queues
		# There is no point wasting processing for
		# other users sorting the messages.
		user_q = self.user_to_queue_map.get(user, None)
		if not user_q:
			raise Exception(f"user has no queue: {user}")
		recipient_q = self.user_to_queue_map.get(recipient, None)
		if not recipient_q:
			raise Exception(f"recipient has no queue: {recipient}")

		# If for some reason the user chose to send a whisper
		# to themself, don't double add
		user_q.put(msg)
		if user == recipient:
			return
		recipient_q.put(msg)


	def send_server_message(self, msg):
		msg = ServerMessage(msg)
		# Server message is for all users logged in.
		for q in self.client_queues:
			q.put(msg)
