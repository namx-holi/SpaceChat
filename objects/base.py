class Object:

	PRIORITY=0
	CHARACTER="?"

	@property
	def terrain(self):
		if self.tile:
			return self.tile.terrain
		return None

	@property
	def x(self):
		if self.tile:
			return self.tile.x
		return None

	@property
	def y(self):
		if self.tile:
			return self.tile.y
		return None

	def __init__(self):#, char, prio):
		# self.PRIORITY = prio
		# self.CHARACTER = char
		self.tile = None

	def describe(self):
		return "A generic object."

	# TODO: Move to terrain manager
	def move_rel(self, delta_x, delta_y):
		if not self.tile:
			raise Exception("tried to move object not on terrain")
		new_x = self.x + delta_x
		new_y = self.y + delta_y

		# Save terrain to reference later
		terrain = self.tile.terrain
		self.tile.remove_object(self)
		terrain.get_tile(new_x, new_y).add_object(self)
