
from uuid import uuid4


class Session:

	@property
	def rover(self):
		return self.user.rover


	def __init__(self, user):
		self.user = user
		self.token = str(uuid4())

		user.session = self

		# Add their rover back to last location
		self.rover.add_to_terrain()

		# Backlog of broadcasts received
		self.broadcasting = False
		self.broadcast_backlog = []


	def close(self):
		self.token = None
		self.user.session = None

		# Remove their rover from terrain
		self.rover.remove_from_terrain()


	def broadcast_generator(self):
		if self.broadcast_backlog:
			yield None
		msg = self.broadcast_backlog.pop(0)
		yield msg
