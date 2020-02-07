
import socket


HOST = "0.0.0.0"
PORT = 7777

class Client:

	def __init__(self):
		...


	def connect(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# TODO: Set a timeout

		s.connect((HOST, PORT))
		self.server = s


	def input_loop(self):
		self.connect()

		while True:
			action = input("> ")
			self.server.send(action.encode())
			response = self.server.recv(1024)
			print(response.decode())


if __name__ == "__main__":
	client = Client()
	client.input_loop()
