
from flask import jsonify
from app.game import bp

from app.helpers import requires_token, uses_fields
from app.helpers import direction_to_delta

from app import message_manager


@bp.route("/api/move", methods=["POST"])
@requires_token
@uses_fields("direction")
def move_rover(session, direction):

	# Translate direction to delta pos
	delta = direction_to_delta(direction)
	if delta is None:
		return jsonify(dict(
			error="invalid direction"
		)), 400

	# Move rover
	session.rover.move_rel(*delta)

	# Return success and position
	return jsonify(dict(
		msg=f"moved {direction.title()}"
	)), 200


@bp.route("/api/observe", methods=["POST"])
@requires_token
def observe(session):

	# Get tiles around rover
	tiles = session.user.rover.observe()

	# Return success, position, and tiles
	return jsonify(dict(
		msg=f"observed at ({session.rover.x},{session.rover.y})",
		tiles=tiles
	)), 200


@bp.route("/api/note", methods=["POST"])
@requires_token
@uses_fields("msg")
def leave_note(session, msg):

	# Check if msg length is under 200 characters
	if len(msg) > 200:
		return jsonify(dict(
			error="msg must be under 200 characters"
		)), 400

	# Create note and have it added to terrain
	session.rover.leave_note(msg)

	# Return success
	return jsonify(dict(
		msg="note left"
	)), 200


@bp.route("/api/inspect", methods=["POST"])
@requires_token
@uses_fields("direction")
def inspect(session, direction):

	# Translate direction to delta pos
	delta = direction_to_delta(direction)
	if delta is None:
		return jsonify(dict(
			error="invalid direction"
		)), 400

	# Get tile
	delta_x, delta_y = delta
	new_x = session.rover.x + delta_x
	new_y = session.rover.y + delta_y
	tile = session.rover.terrain.get_tile(new_x, new_y)

	# Get descriptions of all objects on tile
	content = [obj.describe() for obj in tile.objects]

	# Return success and contents of tile
	return jsonify(dict(
		msg=f"inspecting {direction.title()}",
		objs=content
	)), 200


@bp.route("/api/message", methods=["POST"])
@requires_token
@uses_fields("msg")
def send_message(session, msg):

	# Check if msg length is under 200 characters
	if len(msg) > 200:
		return jsonify(dict(
			error="msg must be under 200 characters"
		)), 400

	# Add message to message manager
	message_manager.send_message(session.user, msg)

	# Return success
	return jsonify(dict(
		msg="message sent"
	)), 200
