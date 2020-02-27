
from flask import jsonify
from app.game import bp

from app.helpers import requires_token, uses_fields
from app.helpers import direction_to_delta
from managers.message_manager import SMail
from app import message_manager, session_manager, user_manager


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


@bp.route("/api/whisper", methods=["POST"])
@requires_token
@uses_fields("recipient", "msg")
def send_whisper(session, recipient, msg):

	# Check if msg length is under 200 characters
	if len(msg) > 200:
		return jsonify(dict(
			error="msg must be under 200 characters"
		)), 400

	# Check if the recipient exists
	recipient = user_manager.get_by_name(recipient)
	if not recipient:
		return jsonify(dict(
			error="recipient does not exist"
		)), 400

	# Check if the recipient is logged in!
	# They cannot receive the message otherwise
	if not session_manager.get_by_user(recipient):
		return jsonify(dict(
			error="user is unable to receive whisper"
		)), 400

	message_manager.send_whisper(session.user, recipient, msg)

	# Return success
	return jsonify(dict(
		msg="whipser sent"
	)), 200


@bp.route("/api/send-smail", methods=["POST"])
@requires_token
@uses_fields("recipient", "subject", "msg")
def send_smail(session, recipient, subject, msg):

	# Check if subject length is under 200 characters
	if len(subject) > 200:
		return jsonify(dict(
			error="subject must be under 200 characters"
		)), 400

	# Check if msg length is under 2000 characters
	if len(msg) > 2000:
		return jsonify(dict(
			error="msg must be under 2000 characters"
		)), 400

	# Check if the recipient exists
	recipient = user_manager.get_by_name(recipient)
	if not recipient:
		return jsonify(dict(
			error="recipient does not exist"
		)), 400

	# Create SMail object and add to the recipients smail list
	smail = SMail(
		sender=session.user,
		recipient=recipient,
		subject=subject,
		msg=msg)
	recipient.smails.append(smail)

	# TODO: Send a message to the recipient to notify they have
	# a new message. Create an AlertMessage class for this in the
	# message manager.

	# Notify the user the SMail has sent successfuly!
	return jsonify(dict(
		msg="SMail sent"
	)), 200


@bp.route("/api/check-smail", methods=["POST"])
@requires_token
def check_smail(session):

	# Check if user has any SMails
	if not session.user.smails:
		return jsonify(dict(
			msg="your SMail inbox is empty"
		)), 200

	# Get all the subjects along with a number
	smails = session.user.smails
	subject_lines = [
		f"{smail_num+1}) {smail.subject}"
		for smail_num, smail in enumerate(smails)]

	# Return the subjects of all SMails
	return jsonify(dict(
		msg=f"you have {len(smails)} SMails",
		subject_lines=subject_lines
	)), 200


@bp.route("/api/read-smail", methods=["POST"])
@requires_token
@uses_fields("smail_id")
def read_smail(session, smail_id):

	# Try turn the smail_id into a number
	if not smail_id.isnumeric():
		return jsonify(dict(
			error="smail_id must be a number"
		)), 400
	smail_id = int(smail_id)

	# Check if the SMail id is valid
	smails = session.user.smails
	if smail_id <= 0 or smail_id > len(smails):
		return jsonify(dict(
			error="invalid smail_id"
		)), 400

	# Get the smail and return it
	smail = smails[smail_id-1] # -1 for index
	return jsonify(dict(
		sender=smail.sender.username,
		subject=smail.subject,
		msg=smail.msg
	)), 200
