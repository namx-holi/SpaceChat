
import json
import requests
import select
import socket
import struct
import threading
import traceback


HOST = "0.0.0.0"
BASE_API_URL = f"http://{HOST}:7777/api"
BROADCAST_HOST = f"{HOST}"
BROADCAST_PORT = 7778


def make_request(endpoint, data):
	url = f"{BASE_API_URL}/{endpoint}"
	r = requests.post(url=url, json=data)
	resp = r.json()
	print(resp)
	print("")
	return resp


def display_tiles(tiles):
	for row in tiles:
		for col in row:
			print(col, end=" ")
		print("")


def read_broadcast_packet(conn):
	len_bytes = conn.recv(4)
	content_len = struct.unpack("I", len_bytes)[0]

	content_bytes = conn.recv(content_len)
	content = content_bytes.decode()
	return json.loads(content)



class Client:

	def __init__(self):
		self.running = False
		self.token = None
		self.logged_in = False

		# Used to read broadcasts!
		self.broadcast_conn = None


	def run(self):
		self.running = True
		while self.running:
			user_input = input("> ")

			try:
				self.handle(user_input)
			except Exception as e:
				traceback.print_exc()


	def handle(self, user_input):
		action, _, args = user_input.partition(" ")
		args = args.strip().split(" ")
		if action == "help":
			self.help()

		elif action == "register":
			username = args[0]
			password = " ".join(args[1:])
			self.register(username, password)

		elif action == "login":
			username = args[0]
			password = " ".join(args[1:])
			self.login(username, password)

		elif action == "move":
			direction = args[0]
			self.move(direction)

		elif action == "observe":
			self.observe()

		elif action == "note":
			msg = " ".join(args)
			self.note(msg)

		elif action == "inspect":
			direction = args[0]
			self.inspect(direction)

		elif action == "message":
			msg = " ".join(args)
			self.message(msg)

		elif action == "logout":
			self.logout()

		elif action == "exit":
			if self.logged_in:
				self.logout()
			self.running = False

		else:
			print("Not valid action!")


	def connect_to_broadcast_server(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((BROADCAST_HOST, BROADCAST_PORT))
		self.broadcast_conn = s

		broadcast_read_thread = threading.Thread(
			target=self.broadcast_read_loop)
		broadcast_read_thread.start()


	def broadcast_read_loop(self):
		# Send our token
		self.broadcast_conn.send(self.token.encode())
		resp = read_broadcast_packet(self.broadcast_conn)
		print(resp)

		if "error" in resp:
			print("ERROR: ", resp)
			return

		while self.logged_in:
			ready = select.select([self.broadcast_conn], [], [], 0.25)
			if ready[0]:
				resp = read_broadcast_packet(self.broadcast_conn)
				print(resp)

		self.broadcast_conn.send("EXIT".encode())
		self.broadcast_conn.close()
		self.broadcast_conn = None


	def help(self):
		data = dict()
		resp = make_request("help", data)

		print("Keys:", resp.keys())
		print("Sorted keys:", sorted(resp.keys()))

		for command in sorted(resp.keys()):
			desc = resp[command]["desc"]
			args = resp[command]["args"]
			requires_token = resp[command]["requires_token"]

			print("{}{}{}".format(
				command,
				"" if not args else " " + " ".join(args),
				"" if not requires_token else " (requires token)"
			))
			print(f"  - {desc}")


		# TODO: Display help in a nice way.


	def register(self, username, password):
		data = dict(username=username, password=password)
		resp = make_request("register", data)


	def login(self, username, password):
		data = dict(username=username, password=password)
		resp = make_request("login", data)
		self.token = resp.get("token", None)
		if self.token:
			self.logged_in = True
			self.connect_to_broadcast_server()


	def move(self, direction):
		data = dict(token=self.token, direction=direction)
		resp = make_request("move", data)


	def observe(self):
		data = dict(token=self.token)
		resp = make_request("observe", data)
		tiles = resp.get("tiles", [])
		display_tiles(tiles)


	def note(self, msg):
		data = dict(token=self.token, msg=msg)
		resp = make_request("note", data)


	def inspect(self, direction):
		data = dict(token=self.token, direction=direction)
		resp = make_request("inspect", data)


	def message(self, msg):
		data = dict(token=self.token, msg=msg)
		resp = make_request("message", data)


	def logout(self):
		data = dict(token=self.token)
		resp = make_request("logout", data)
		self.logged_in = False


print("Type 'exit' to exit the client.")
client = Client()
client.run()
print("Exited!")
