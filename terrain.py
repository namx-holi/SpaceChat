
from rover import Rover


class Terrain:

	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.map = [
			[[] for _ in range(width)]
			for _ in range(height)]


	def get_square(self, x, y):
		"""Returns the list of objects at point (x,y).
		"""

		return self.map[y % self.height][x % self.width]


	def add_object(self, obj, x, y):
		"""Adds an object to the square at (x,y).
		"""

		self.get_square(x,y).append(obj)
		obj.x = x % self.width
		obj.y = y % self.height
		obj.terrain = self


	def remove_object(self, obj):
		"""Removes the given object from the terrain.
		"""

		# TODO: Check if the object is even on the terrain first

		self.get_square(obj.x, obj.y).remove(obj)
		obj.x = None
		obj.y = None
		obj.terrain = None

		# TODO: Return a value to indicate it failed or succeeded
