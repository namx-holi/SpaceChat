class Object:
	PRIORITY = 0
	CHARACTER = "?"

	def __init__(self):
		self.x = 0
		self.y = 0
		self.terrain = None
		self.tile = None


	def show(self):
		self.terrain.add_object(self, self.x, self.y)


	def hide(self):
		self.terrain.remove_object(self)


	def describe(self):
		return "A generic object."


	# TODO: Move to terrain manager?
	def move_rel(self, delta_x, delta_y):
		if not self.terrain:
			raise Exception("No terrain to move on")

		new_x = (self.x + delta_x) % self.terrain.width
		new_y = (self.y + delta_y) % self.terrain.height

		if self.tile:
			# Refresh by remove and replace
			self.terrain.remove_object(self)
			self.terrain.add_object(self, new_x, new_y)

		self.x = new_x
		self.y = new_y
