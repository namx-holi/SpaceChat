
from flask import request, jsonify
import functools
from app import session_manager

# TODO: Move settings to a settings file!
from managers.session_manager import INACTIVITY_TIMEOUT_TIME


def requires_token(func):
	"""
	Decorator that checks if a valid token has been given.
	"""

	@functools.wraps(func)
	def inner(*args, **kwargs):
		# Check if any json request
		if not request.json or "token" not in request.json:
			return jsonify(dict(
				error="missing token field"
			)), 400

		# Get token and check if non empty
		token = request.json.get("token", None)
		if not token:
			return jsonify(dict(
				error="missing token field"
			)), 400

		# Check if the token corresponds to a session
		session = session_manager.get_by_token(token)
		if not session:
			return jsonify(dict(
				error="invalid token"
			)), 400

		# Check if the session has timed out due to inactivity
		if session.timed_out():
			session.close()
			return jsonify(dict(
				error="session timed out (inactive for {} minutes)".format(
					INACTIVITY_TIMEOUT_TIME)
			)), 400

		# Update the last active time
		session.update_last_active()

		# Call the original func
		return func(session, *args, **kwargs)
	return inner



def uses_fields(*fields):
	"""
	Decorator that checks if all required fields are present.
	"""

	def actual_decorator(func):
		@functools.wraps(func)
		def inner(*args, **kwargs):

			# Check if any json request
			if not request.json:
				# When missing all fields, default to asking for
				# the first field.
				return jsonify(dict(
					error=f"missing {fields[0]} field"
				)), 400

			# For each field, check if it contains the field
			for field in fields:
				# If the field is in any way empty, it's ignored.
				if not request.json.get(field, None):
					return jsonify(dict(
						error=f"missing {field} field"
					)), 400

				# TODO: Check if field is a string

			# Construct args into the fields
			new_args = [*args] # Copy the old args!
			for field in fields:
				new_args.append(request.json[field])

			# Call the original func
			return func(*new_args, **kwargs)

		return inner
	return actual_decorator



def direction_to_delta(direction):
	direction = direction.title()
	if direction == "North":
		return (0, -1)
	elif direction == "East":
		return (+1, 0)
	elif direction == "South":
		return (0, +1)
	elif direction == "West":
		return (-1, 0)
	else:
		return None
