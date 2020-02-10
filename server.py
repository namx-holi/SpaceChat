
from flask import Flask, request, abort, jsonify
from flask import stream_with_context, Response
import functools
import time

from session import Session
from terrain import Terrain
from user import User


app = Flask(__name__)


users = {}
sessions = {}
terrain = Terrain(20, 20)


@app.route("/")
def index():
	return "TODO: Make a page for game!"


def requires_token(func):
	@functools.wraps(func)
	def wrapper_requires_token(*args, **kwargs):
		if not request.json or "token" not in request.json:
			return jsonify(dict(
				error="Missing token field"
			)), 400

		token = request.json["token"]

		if token not in sessions:
			return jsonify(dict(
				error="Invalid token"
			)), 400

		return func(*args, **kwargs)
	return wrapper_requires_token



# Register endpoint
# Should allow users to post their desired username and password hash.
# These should be stored into a db.
@app.route("/api/register", methods=["POST"])
def register_user():
	if not request.json:
		return jsonify(dict(
			error="Missing username and password field"
		)), 400
	if "username" not in request.json:
		return jsonify(dict(
			error="Missing username field"
		)), 400
	if "password" not in request.json:
	 	return jsonify(dict(
	 		error="Missing password field"
	 	)), 400

	username = request.json["username"]
	password = request.json["password"]

	# Check if user exists
	if username in users:
		return jsonify(dict(
			error=f"User {username} already exists"
		)), 400

	# Create user, respond with success
	user = User(username)
	user.set_password(password)
	users[username] = user

	# Register users rover to default terrain
	terrain.register_object(user.rover)

	return jsonify(dict(
		msg=f"User {user.name} created!"
	)), 200



# Login endpoint
# Users post their username and password hash. They are given a token.
# A session is created for this user.
# This token is used for other endpoints.
@app.route("/api/login", methods=["POST"])
def login_user():
	if not request.json:
		return jsonify(dict(
			error="Missing username and password field"
		)), 400
	if "username" not in request.json:
		return jsonify(dict(
			error="Missing username field"
		)), 400
	if "password" not in request.json:
		return jsonify(dict(
			error="Missing password field"
		)), 400

	username = request.json["username"]
	password = request.json["password"]

	# Check if user exists
	if username not in users:
		return jsonify(dict(
			error=f"User {username} doesn't exist"
		)), 400

	# Check password
	user = users[username]
	if not user.check_password(password):
		return jsonify(dict(
			error="Incorrect password"
		)), 400

	# Check if user already logged in. If so, return current token
	if user.session:
		return jsonify(dict(
			msg=f"User {username} logged in!",
			token=f"{user.session.token}"
		)), 200

	# Create session, store session, return token
	session = Session(user)
	sessions[session.token] = session
	return jsonify(dict(
		msg=f"User {username} logged in!",
		token=f"{session.token}"
	)), 200



# Move endpoint
# Users post their desired direction, along with their token.
# Their rover is moved in that direction if valid.
@app.route("/api/move", methods=["POST"])
@requires_token
def move_rover():
	if "direction" not in request.json:
		return jsonify(dict(
			error="Missing direction field"
		)), 400

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
			error="Invalid direction"
		)), 400

	return jsonify(dict(
		msg=f"Moved {direction.title()}"
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
		msg=f"Observed at ({session.rover.x},{session.rover.y})",
		tiles=tiles
	)), 200



# Note endpoint
# Users can leave a note at their current location.
@app.route("/api/note", methods=["POST"])
@requires_token
def leave_note():
	if "msg" not in request.json:
		return jsonify(dict(
			error="Missing msg field"
		)), 400

	token = request.json["token"]
	session = sessions[token]

	msg = request.json["msg"]
	session.rover.leave_note(msg)

	return jsonify(dict(
		msg="Note left"
	)), 200



# Inspect endpoint
# Users can look at a tile in a direction from themself.
@app.route("/api/inspect", methods=["POST"])
@requires_token
def inspect():
	if "direction" not in request.json:
		return jsonify(dict(
			error="Missing direction field"
		)), 400

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
			error="Invalid direction"
		)), 400

	return jsonify(dict(
		msg=f"Inspecting {direction}",
		objs=content
	)), 200



# # Broadcast endpoint
# # Constantly downloads broadcasts!
# @app.route("/api/broadcast", methods=["GET"])
# @requires_token
# def read_broadcast():
# 	token = request.json["token"]
# 	session = sessions[token]

# 	session.broadcasting = True

# 	def generate():
# 		print("Starting generator")
# 		while True:
# 			print("Checking if broadcast backlog")
# 			print(session.broadcast_backlog)
# 			if session.broadcast_backlog:
# 				msg = session.broadcast_backlog.pop(0)
# 				print("Yielding msg:", repr(msg))
# 				yield msg + "\n"
# 			time.sleep(1)

# 	return Response(generate(), content_type="text/event-stream")
# 	print("Poooo")



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
		msg="Logged out!"
	)), 200



# # Test method
# def broadcast_loop():
# 	import time
	
# 	ticks = 0
# 	while True:
# 		print("Adding message to backlocks")
# 		for session_token in sessions:
# 			session = sessions[session_token]

# 			if session.broadcasting:
# 				session.broadcast_backlog.append(f"Time: {ticks}")

# 		ticks += 1
# 		time.sleep(5)


if __name__ == "__main__":
	import threading

	# # Start a broadcast loop thread
	# broadcast_loop_thread = threading.Thread(
	# 	target=broadcast_loop)
	# broadcast_loop_thread.start()

	app.run(debug=False)
