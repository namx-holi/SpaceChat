from objects.base import Object
from objects.note import Note


class Rover(Object):

	PRIORITY=100
	CHARACTER="R"

	def __init__(self, user):
		super().__init__()

		# Bind to user and make backref
		self.user = user
		user.rover = self

		# Number of tiles distance the rover can observe
		self.view_range = 2


	def describe(self):
		return f"{self.user.username}'s rover."


	# TODO: Move to endpoint logic
	def observe(self):
		# +1 for range because range works like [start, end)
		x_min = self.x - self.view_range
		x_max = self.x + self.view_range + 1
		y_min = self.y - self.view_range
		y_max = self.y + self.view_range + 1

		tile_characters = []
		for y in range(y_min, y_max):
			row = []
			for x in range(x_min, x_max):
				tile = self.tile.terrain.get_tile(x,y)
				row.append(tile.as_character())
			tile_characters.append(row)

		return tile_characters


	# TODO: Move to endpoint logic
	def leave_note(self, msg):
		# We don't need to use the returned Note as
		# on initialisation, it adds itself to the
		# tile this rover is on!
		_ = Note(self.user, msg)
