
from flask import jsonify
from app.game import bp

from app.helpers import requires_token, uses_fields
from app import (
	session_manager,
	terrain_manager,
	user_manager
)

from objects.rover import Rover



@bp.route("/api/register", methods=["POST"])
@uses_fields("username", "password")
def register_user(username, password):

	# Check if user exists
	if user_manager.get_by_name(username):
		return jsonify(dict(
			error=f"user '{username}' already exists"
		)), 400

	# Create user
	user = user_manager.create_user(username)
	user.set_password(password)

	# Set rover's terrain to default terrain
	user.rover.terrain = terrain_manager.default_terrain

	# Return success
	return jsonify(dict(
		msg=f"user '{user.username}' registered"
	)), 200


@bp.route("/api/login", methods=["POST"])
@uses_fields("username", "password")
def login_user(username, password):

	# Check if user exists
	user = user_manager.get_by_name(username)
	if not user:
		return jsonify(dict(
			error=f"user '{username}' doesn't exist"
		)), 400

	# Check password
	if not user.check_password(password):
		return jsonify(dict(
			error="incorrect password"
		)), 400

	# Check if session exists. If so,
	# Invalidate old token and remove session
	if user.session:
		user.session.close()

	# Create new session for user
	session = session_manager.create_session(user)

	# Return success and token
	return jsonify(dict(
		msg=f"user '{username}' logged in",
		token=f"{session.token}"
	)), 200


@bp.route("/api/logout", methods=["POST"])
@requires_token
def logout_user(session):

	# Invalidate old token and remove session
	session.close()

	# Return success
	return jsonify(dict(
		msg="logged out"
	)), 200
