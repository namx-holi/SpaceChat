
from movable_object import MovableObject
from note import Note


class Rover(MovableObject):

	def __init__(self, user):
		super().__init__()
		self.user = user
		self.view_range = 2


	def describe(self):
		return f"{self.user.name}'s rover."


	def observe(self):

		# +1 for range because range works like [start, end)
		x_min = self.x - self.view_range
		x_max = self.x + self.view_range + 1
		y_min = self.y - self.view_range
		y_max = self.y + self.view_range + 1

		tiles = []
		for y in range(y_min, y_max):
			row = []
			for x in range(x_min, x_max):
				objs = self.terrain.get_square(x,y)

				if any([isinstance(obj, Rover) for obj in objs]):
					row.append("X")
				elif any([isinstance(obj, Note) for obj in objs]):
					row.append("M")
				else:
					row.append("-")

			tiles.append(row)

		return tiles


	def leave_note(self, msg):
		note = Note(self.user, msg)
		self.terrain.register_object(note)
		self.terrain.add_object(note, self.x, self.y)


	def inspect(self, rel_x, rel_y):
		x = self.x + rel_x
		y = self.y + rel_y
		objs = self.terrain.get_square(x,y)
		return [obj.describe() for obj in objs]
