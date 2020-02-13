
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


	def close(self):
		self.token = None
		self.user.session = None

		# Remove their rover from terrain
		self.rover.remove_from_terrain()
