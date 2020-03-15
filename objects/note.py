from objects.base import Object


class Note(Object):

	PRIORITY=50
	CHARACTER="M"

	def __init__(self, user, msg):
		super().__init__()

		# Bind to user and make backref
		self.user = user
		user.notes.add(self)

		# Add content
		self.msg = msg

		# Add to terrain of users rover
		user.rover.tile.add_object(self)


	def describe(self):
		return f"{self.user.username}'s note. It says '{self.msg}'"
