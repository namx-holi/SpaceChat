
class Note:

	def __init__(self, msg):
		self.msg = msg


	def describe(self):
		return f"A note. It says `{self.msg}`"