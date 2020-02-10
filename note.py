
class Note:

	def __init__(self, user, msg):
		self.user = user
		self.msg = msg

	def describe(self):
		return f"{self.user.name}'s note. It says `{self.msg}`"
