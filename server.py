import socket
import threading

from rover import Rover
from terrain import Terrain
from user import User
from user_interface import UserInterface


class ChatServer:

	def __init__(self):
		self.terrain = Terrain(20, 20)
		self.users = {}


	def run(self, **kwargs):
		"""Starts the server.
		"""

		host = kwargs.get("host", "0.0.0.0")
		port = kwargs.get("port", 7777)

		# Set up socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((host, port))
		
		# Start listening and handle connections
		server.listen(20)
		print(f" [*] Listening on {host}:{port}")
		self.handle_client_connections(server)

		# Once done, close socket
		print(f" [*] Server shutting down")
		server.shutdown(socket.SHUT_RDWR)
		server.close()


	def handle_client_connections(self, server):
		"""
		Method to accept connections and pass them on to their
		client handling threads.
		"""

		while True:
			try:
				conn, addr = server.accept()
			except KeyboardInterrupt:
				print("\n\r [*] Shutting down server...")
				return

			print(f" [*] Client connecting from {addr[0]}:{addr[1]}")
			client_handler_thread = threading.Thread(
				target=self.client_handler,
				args=[conn, addr])
			client_handler_thread.start()


	def client_handler(self, conn, addr):
		"""
		Client handling thread. Performs all interaction with the
		clients.
		"""

		user = self.login_user(conn)
		print(user)
		if not user:
			conn.send(b"Failed login.")
			print(f" [*] Client from {addr[0]}:{addr[1]} failed to log in.")
			conn.close()
			return
		else:
			conn.send(b"Logged in!.")

		# TODO: Have a way to end these on server shutdown
		self.terrain.add_object(user.rover, 0, 0)
		user_interface = UserInterface(user.rover)

		# TODO: Dynamically read bytes
		while True:
			user_input = conn.recv(1024)
			result = user_interface.parse_action(user_input.decode())

			if result is None:
				break

			# TODO: Handle when result is None

			conn.send(result.encode())

		print(f" [*] Ending client connection from {addr[0]}:{addr[1]}")
		self.terrain.remove_object(user.rover)
		conn.close()


	def login_user(self, conn):
		# Read login string?
		user_input = ""

		while True:
			user_input = conn.recv(1024).decode()

			if user_input == "exit":
				return

			if (
				user_input.startswith("login")
				or user_input.startswith("register")
			):
				break

			
			conn.send(b"Please log in with `login <user> <pword>`,"+
				b"or register with `register <user> <pword>`.")

		action, _, args = user_input.partition(" ")
		username, _, pword = args.partition(" ")
		# TODO: Handle password

		print(action)
		print(username)
		print(pword)

		if action == "register":
			user = User(username)
			self.users[username] = user
			return user

		return self.users.get(username, None)





if __name__ == "__main__":
	server = ChatServer()
	server.run()
