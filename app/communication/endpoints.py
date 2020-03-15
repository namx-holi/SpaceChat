
from flask import jsonify
from app.communication import bp

from app.helpers import requires_token, uses_fields
from app import message_manager, user_manager


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
	if not recipient.session:
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

	# Send a smail!
	message_manager.send_smail(session.user, recipient, subject, msg)

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
			msg="your SMail inbox is empty",
			smails=[]
		)), 200

	# Get all the subjects along with a number
	smail_info = [
		dict(
			id=smail_num+1,
			sender=smail.sender.username,
			subject=smail.subject
		) for smail_num, smail in enumerate(session.user.smails)]

	# Return the subjects of all SMails
	return jsonify(dict(
		msg=f"you have {len(smail_info)} SMails",
		smails=smail_info
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


@bp.route("/api/delete-smail", methods=["POST"])
@requires_token
@uses_fields("smail_id")
def delete_smail(session, smail_id):

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

	# Pop the smail and return success
	_ = smails.pop(smail_id-1) # -1 for index
	return jsonify(dict(
		msg="SMail deleted"
	)), 200


@bp.route("/api/add-friend", methods=["POST"])
@requires_token
@uses_fields("user")
def add_friend(session, user):

	# Check if the user exists
	user = user_manager.get_by_name(user)
	if not user:
		return jsonify(dict(
			error="user does not exist"
		)), 400

	# Check if user is self. That doesn't make sense!
	if user == session.user:
		return jsonify(dict(
			error="cannot add self as friend"
		)), 400

	# Check if user is already a friend
	if user in session.user.friends:
		return jsonify(dict(
			error="user already on friend list"
		)), 400

	# Send an alert to the user if they are logged in
	if user.session:
		message_manager.send_alert(user,
			f"{session.user.username} has added you as a friend")

	# Add the recipient to the users friend list
	session.user.friends.add(user)

	# Return success
	return jsonify(dict(
		msg=f"{user.username} added to friends list"
	)), 200


@bp.route("/api/remove-friend", methods=["POST"])
@requires_token
@uses_fields("user")
def remove_friend(session, user):

	# Check if the user exists
	user = user_manager.get_by_name(user)
	if not user:
		return jsonify(dict(
			error="user does not exist"
		)), 400

	# Check if user is in friend list
	if user not in session.user.friends:
		return jsonify(dict(
			error="user not in friends list"
		)), 400

	# NOTE: Do not send an alert for the user being
	# removed as a friend!

	# Remove the user from friends list
	session.user.friends.remove(user)

	# Return success
	return jsonify(dict(
		msg=f"{user.username} removed from friends list"
	)), 200


@bp.route("/api/view-friends", methods=["POST"])
@requires_token
def view_friends(session):

	print("Doing a thing")

	# Check if user has any friends
	if not session.user.friends:
		return jsonify(dict(
			msg="your friends list is empty",
			friends=[]
		)), 200

	# Get all friends along with online status
	# Count online users too
	friends_info = []
	online_count = 0
	for friend in session.user.friends:
		# Only give status if mutual friends
		if session.user in friend.friends:
			online = (friend.session is not None)
		else:
			online = None

		if online:
			online_count += 1

		friends_info.append(dict(
			username=friend.username,
			online=online
		))

	# Return the friends list
	return jsonify(dict(
		msg=f"you have {online_count} friends online",
		friends=friends_info
	)), 200
