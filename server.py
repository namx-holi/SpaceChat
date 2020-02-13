
from flask import Flask, request, abort, jsonify
from flask import stream_with_context, Response
import functools
import time

from session import Session
from terrain import Terrain
from user import User

from message_manager import MessageManager
from message_manager import Message, ServerMessage


app = Flask(__name__)


users = {}
sessions = {}
terrain = Terrain(20, 20)


# For broadcasts
msg_manager = MessageManager(sessions)
msg_manager.start(7778)


# TODO: Helper to translate direction to rel pos


@app.route("/")
def index():
	return "TODO: Make a page for game!"



def requires_token(func):
	@functools.wraps(func)
	def inner(*args, **kwargs):
		if not request.json or "token" not in request.json:
			return jsonify(dict(
				error="missing token field"
			)), 400

		token = request.json["token"]

		if token not in sessions:
			return jsonify(dict(
				error="invalid token"
			)), 400

		return func(*args, **kwargs)
	return inner


def requires_fields(*fields):
	def actual_decorator(func):
		@functools.wraps(func)
		def inner(*args, **kwargs):
			if not request.json:
				# When missing all fields, default to
				# asking for first.
				return jsonify(dict(
					error=f"missing {fields[0]} field"
				)), 400

			for field in fields:
				# If the field is in any way empty!
				if not request.json.get(field, None):
					return jsonify(dict(
						error=f"missing {field} field"
					)), 400

				# TODO: Check if all string!

			# All fields satisfied!
			return func(*args, **kwargs)
		return inner
	return actual_decorator



# Register endpoint
# Should allow users to post their desired username and password hash.
# These should be stored into a db.
@app.route("/api/register", methods=["POST"])
@requires_fields("username", "password")
def register_user():
	username = request.json["username"]
	password = request.json["password"]

	# Check if user exists
	if username in users:
		return jsonify(dict(
			error=f"user '{username}' already exists"
		)), 400

	# Create user, respond with success
	user = User(username)
	user.set_password(password)
	users[username] = user

	# Register users rover to default terrain
	terrain.register_object(user.rover)

	return jsonify(dict(
		msg=f"user '{user.name}' registered"
	)), 200



# Login endpoint
# Users post their username and password hash. They are given a token.
# A session is created for this user.
# This token is used for other endpoints.
@app.route("/api/login", methods=["POST"])
@requires_fields("username", "password")
def login_user():
	username = request.json["username"]
	password = request.json["password"]

	# Check if user exists
	if username not in users:
		return jsonify(dict(
			error=f"user '{username}' doesn't exist"
		)), 400

	# Check password
	user = users[username]
	if not user.check_password(password):
		return jsonify(dict(
			error="incorrect password"
		)), 400

	# Check if user already logged in. If so, return current token
	if user.session:
		return jsonify(dict(
			msg=f"user '{username}' logged in",
			token=f"{user.session.token}"
		)), 200

	# Create session, store session, return token
	session = Session(user)
	sessions[session.token] = session
	return jsonify(dict(
		msg=f"user '{username}' logged in",
		token=f"{session.token}"
	)), 200



# Move endpoint
# Users post their desired direction, along with their token.
# Their rover is moved in that direction if valid.
@app.route("/api/move", methods=["POST"])
@requires_token
@requires_fields("direction")
def move_rover():
	token = request.json["token"]
	session = sessions[token]

	direction = request.json["direction"].title()
	if direction == "North":
		session.rover.move_rel(0, -1)
	elif direction == "East":
		session.rover.move_rel(+1, 0)
	elif direction == "South":
		session.rover.move_rel(0, +1)
	elif direction == "West":
		session.rover.move_rel(-1, 0)
	else:
		return jsonify(dict(
			error="invalid direction"
		)), 400

	return jsonify(dict(
		msg=f"moved {direction.title()}"
	)), 200



# Observe endpoint
# Users can observe what is around their rover.
@app.route("/api/observe", methods=["POST"])
@requires_token
def observe():
	token = request.json["token"]
	session = sessions[token]

	tiles = session.rover.observe()
	return jsonify(dict(
		msg=f"observed at ({session.rover.x},{session.rover.y})",
		tiles=tiles
	)), 200



# Note endpoint
# Users can leave a note at their current location.
@app.route("/api/note", methods=["POST"])
@requires_token
@requires_fields("msg")
def leave_note():
	msg = request.json["msg"]
	if len(msg) > 200:
		return jsonify(dict(
			error="msg must be under 200 characters"
		)), 400

	token = request.json["token"]
	session = sessions[token]

	session.rover.leave_note(msg)

	return jsonify(dict(
		msg="note left"
	)), 200



# Inspect endpoint
# Users can look at a tile in a direction from themself.
@app.route("/api/inspect", methods=["POST"])
@requires_token
@requires_fields("direction")
def inspect():
	token = request.json["token"]
	session = sessions[token]

	direction = request.json["direction"].title()
	if direction == "North":
		content = session.rover.inspect(0, -1)
	elif direction == "East":
		content = session.rover.inspect(+1, 0)
	elif direction == "South":
		content = session.rover.inspect(0, +1)
	elif direction == "West":
		content = session.rover.inspect(-1, 0)
	else:
		return jsonify(dict(
			error="invalid direction"
		)), 400

	return jsonify(dict(
		msg=f"inspecting {direction}",
		objs=content
	)), 200



# Message endpoint
# Allows users to send a message to the whole world!
@app.route("/api/message", methods=["POST"])
@requires_token
@requires_fields("msg")
def message():
	msg = request.json["msg"]
	if len(msg) > 200:
		return jsonify(dict(
			error="msg must be under 200 characters"
		)), 400

	token = request.json["token"]
	session = sessions[token]
	username = session.user.name

	msg = Message(username, msg)
	print("Sending", msg)
	msg_manager.send_to_all(msg)

	return jsonify(dict(
		msg="message sent",
	)), 200



# Logout endpoint
# Users post their token. Their session is closed.
# The token is invalidated.
@app.route("/api/logout", methods=["POST"])
@requires_token
def logout_user():
	token = request.json["token"]
	session = sessions[token]

	# Remove the current token
	session.close()
	del sessions[token]

	return jsonify(dict(
		msg="logged out"
	)), 200



# Test method
def broadcast_loop():
	import time
	
	ticks = 0
	while True:
		msg = ServerMessage(f"Time: {ticks}")
		print("Broadcasting message", msg)
		msg_manager.send_to_all(msg)

		ticks += 1
		time.sleep(5)



if __name__ == "__main__":
	import threading

	# Start a broadcast loop thread
	broadcast_loop_thread = threading.Thread(
		target=broadcast_loop)
	broadcast_loop_thread.start()

	app.run(port=7777, debug=False)
