
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


	def move_object(self, obj, direction):
		direction = direction.lower()
		if direction in ["n"]:
			self.get_square(obj.x, obj.y).remove(obj)
			self.add_object(obj, obj.x, obj.y-1)

		elif direction in ["e"]:
			self.get_square(obj.x, obj.y).remove(obj)
			self.add_object(obj, obj.x+1, obj.y)

		elif direction in ["s"]:
			self.get_square(obj.x, obj.y).remove(obj)
			self.add_object(obj, obj.x, obj.y+1)

		elif direction in ["w"]:
			self.get_square(obj.x, obj.y).remove(obj)
			self.add_object(obj, obj.x-1, obj.y)

		else:
			# TODO: raise exception
			print("Error in move direction")
			return


	def display(self):

		# TODO: Class for user interface. Can move imports to the
		# interface then

		for row in range(self.height):
			for col in range(self.width):

				objs = self.map[row][col]
				if any([isinstance(obj, Rover) for obj in objs]):
					print("X ", end="")

				else:
					print("- ", end="")

			print("")

