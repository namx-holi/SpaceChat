

class MovableObject:

	def __init__(self, terrain, x, y):
		self.terrain = terrain
		self.terrain.add_object(self, x, y)


	def move(self, x, y):
		# Save terrain so we can still reference it
		terr = self.terrain

		self.terrain.remove_object(self)
		terr.add_object(self, x, y)


	def move_rel(self, delta_x, delta_y):
		new_x = self.x + delta_x
		new_y = self.y + delta_y
		terr = self.terrain
		self.move(new_x, new_y)
