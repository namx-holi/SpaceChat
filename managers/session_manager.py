from datetime import datetime
from uuid import uuid4

from config import SessionConfig as sessconf



class Session:

	@property
	def rover(self):
		return self.user.rover
	

	def __init__(self, manager, user):
		self.manager = manager
		self.user = user
		self.token = str(uuid4())
		user.session = self

		# Last active on session create
		self.last_active = datetime.now()

		# Show rover
		self.rover.show()

		# Send online mutual friends a login alert!
		for friend in self.user.friends:
			if self.user in friend.friends and friend.session is not None:
				self.manager.message_manager.send_alert(friend,
					f"{self.user.username} logged in!")


	def close(self):
		# Send online mutual friends a logout alert!
		for friend in self.user.friends:
			if self.user in friend.friends and friend.session is not None:
				self.manager.message_manager.send_alert(friend,
					f"{self.user.username} logged out.")

		self.manager.remove_session(self)

		# Hide rover
		self.rover.hide()


	def timed_out(self):
		delta = datetime.now() - self.last_active
		# times 60 because inactivity timeout time is in minutes
		return (delta.total_seconds() > sessconf.INACTIVITY_TIMEOUT_TIME*60)


	def update_last_active(self):
		self.last_active = datetime.now()



class SessionManager:

	def __init__(self):
		self.sessions_by_token = {}
		self.sessions_by_user = {}


	def create_session(self, user):
		session = Session(self, user)
		self.sessions_by_token[session.token] = session
		self.sessions_by_user[user] = session
		return session


	def get_by_token(self, token):
		return self.sessions_by_token.get(token, None)
	def get_by_user(self, user):
		return self.sessions_by_user.get(user, None)


	def remove_session(self, session):
		if session.manager != self:
			# Wrong manager? Error!
			# TODO: Write better error
			raise Exception("session doesn't belong to manager")

		token = session.token
		user = session.user

		del self.sessions_by_token[token]
		del self.sessions_by_user[user]

		session.manager = None
		session.token = None

		user.session = None
