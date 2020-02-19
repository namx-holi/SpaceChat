

class TerrainTile:

	def __init__(self, terrain, x, y):
		self.terrain = terrain
		self.x = x
		self.y = y
		self.objects = []


	def add_object(self, obj):
		self.objects.append(obj)
		obj.tile = self


	def remove_object(self, obj):
		if obj not in self.objects:
			raise Exception(f"{obj} not in object list")
		self.objects.remove(obj)
		obj.tile = None


	def as_character(self):
		if not self.objects:
			return "-"

		highest_prio_obj = self.objects[0]
		for obj in self.objects[1:]:
			if obj.PRIORITY > highest_prio_obj.PRIORITY:
				highest_prio_obj = obj

		return highest_prio_obj.CHARACTER



class Terrain:

	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.tiles = [
			[TerrainTile(self, x,y)
			for x in range(width)]
			for y in range(height)]


	def get_tile(self, x, y):
		return self.tiles[y % self.height][x % self.width]


	def add_object(self, obj, x, y):
		print("Adding obj", obj, "at", x, y)
		self.get_tile(x,y).add_object(obj)


	def remove_object(self, obj):
		if obj.tile.terrain != self:
			raise Exception("obj not on terrain")
		obj.tile.remove_object(obj)



class TerrainManager:

	@property
	def default_terrain(self):
		return self.terrains[0]
	

	def __init__(self):
		self.terrains = [Terrain(20, 20)]


	def add_object_to_default(self, obj):
		self.default_terrain.add_object(obj, 0, 0)


	# TODO: Get a terrain by id