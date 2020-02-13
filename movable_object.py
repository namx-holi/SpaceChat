

class MovableObject:

	def __init__(self):
		self.x = None
		self.y = None
		self.terrain = None


	def add_to_terrain(self):
		self.terrain.add_object(self, self.x, self.y)
	def remove_from_terrain(self):
		self.terrain.remove_object(self)


	def move(self, x, y):
		"""Moves the object to position (x,y) on it's terrain
		"""

		# Save terrain so we can still reference it
		self.terrain.remove_object(self)
		self.terrain.add_object(self, x, y)


	def move_rel(self, delta_x, delta_y):
		"""Moves the object a number of spaces from its current position
		"""

		new_x = self.x + delta_x
		new_y = self.y + delta_y
		self.move(new_x, new_y)
