import socket
import threading

from rover import Rover
from terrain import Terrain
from user_interface import UserInterface


class ChatServer:

	def __init__(self):
		self.terrain = Terrain(20, 20)


	def run(self, **kwargs):
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
		server.shutdown(socket.SHUT_RDWR)
		server.close()


	def handle_client_connections(self, server):
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
		# TODO: Have a way to end these on server shutdown
		rover = Rover(self.terrain, 0, 0)
		user_interface = UserInterface(rover)

		# TODO: Dynamically read bytes
		while True:
			user_input = conn.recv(1024)
			result = user_interface.parse_action(user_input.decode())

			if result is None:
				break

			# TODO: Handle when result is None

			conn.send(result.encode())

		print(f" [*] Ending client connection from {addr[0]}:{addr[1]}")
		self.terrain.remove_object(rover)



if __name__ == "__main__":
	server = ChatServer()
	server.run()
