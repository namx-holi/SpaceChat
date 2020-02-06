

class MovableObject:

	def __init__(self, terrain):
		self.terrain = terrain


	def move(self, direction):
		self.terrain.move_object(self, direction)