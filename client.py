
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
	try:
		resp = r.json()
	except Exception as e:
		print(r.text)
		raise e
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
		# Ignore empty input
		if user_input.strip() == "":
			return

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

		elif action == "whisper":
			recipient = args[0]
			msg = " ".join(args[1:])
			self.whisper(recipient, msg)

		elif action == "send-smail":
			recipient = args[0]
			subject_and_content = " ".join(args[1:])
			subject, _, msg = subject_and_content.partition("|")
			self.send_smail(recipient, subject, msg)

		elif action == "check-smail":
			self.check_smail()

		elif action == "read-smail":
			smail_id = args[0]
			self.read_smail(smail_id)

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
				print("Received message:", resp)

		self.broadcast_conn.send("EXIT".encode())
		self.broadcast_conn.close()
		self.broadcast_conn = None


	def help(self):
		# TODO: Write a help message for commands
		# The reason this will become client-fat is
		# because the client will eventually pivot to
		# a UI where only the api requests will be
		# sent without the need for manual commands
		print("STUB: Help message. Oops!")


	def register(self, username, password):
		data = dict(username=username, password=password)
		resp = make_request("register", data)


	def login(self, username, password):
		if self.logged_in:
			self.logout()

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


	def whisper(self, recipient, msg):
		data = dict(token=self.token, recipient=recipient, msg=msg)
		resp = make_request("whisper", data)


	def send_smail(self, recipient, subject, msg):
		data = dict(token=self.token,
			recipient=recipient, subject=subject, msg=msg)
		resp = make_request("send-smail", data)


	def check_smail(self):
		data = dict(token=self.token)
		resp = make_request("check-smail", data)


	def read_smail(self, smail_id):
		data = dict(token=self.token, smail_id=smail_id)
		resp = make_request("read-smail", data)


	def logout(self):
		data = dict(token=self.token)
		resp = make_request("logout", data)
		self.logged_in = False


print("Type 'exit' to exit the client.")
client = Client()
client.run()
print("Exited!")
