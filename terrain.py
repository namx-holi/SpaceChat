

class Terrain:

	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.map = [
			[[] for _ in range(width)]
			for _ in range(height)]


	def get_square(self, x, y):
		return self.map[y % self.height][x % self.width]


	def register_object(self, obj):
		obj.terrain = self
		obj.x = 0
		obj.y = 0


	def unregister_object(self, obj):
		obj.terrain = None
		obj.x = None
		obj.y = None


	def add_object(self, obj, x, y):
		self.get_square(x,y).append(obj)
		obj.x = x % self.width
		obj.y = y % self.height


	def remove_object(self, obj):
		# TODO: Check if the object is even on the terrain
		self.get_square(obj.x, obj.y).remove(obj)
