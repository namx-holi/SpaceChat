
from rover import Rover


class Terrain:

	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.map = [
			[[] for _ in range(width)]
			for _ in range(height)]


	def get_square(self, x, y):
		return self.map[y % self.height][x % self.width]


	def add_object(self, obj, x, y):
		self.get_square(x,y).append(obj)
		obj.x = x % self.width
		obj.y = y % self.height
		obj.terrain = self


	def remove_object(self, obj):
		self.get_square(obj.x, obj.y).remove(obj)
		obj.x = None
		obj.y = None
		obj.terrain = None


	def display(self):
		# Displays whole map
		for row in range(self.height):
			for col in range(self.width):

				objs = self.map[row][col]
				if any([isinstance(obj, Rover) for obj in objs]):
					print("X ", end="")

				else:
					print("- ", end="")

			print("")
