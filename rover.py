
from movable_object import MovableObject
from note import Note


class Rover(MovableObject):

	def __init__(self, terrain, x, y):
		super().__init__(terrain, x, y)
		self.view_range = 2


	def describe(self):
		return "A rover."


	def observe(self):

		# +1 for range because range works like [start, end)
		x_min = self.x - self.view_range
		x_max = self.x + self.view_range + 1
		y_min = self.y - self.view_range
		y_max = self.y + self.view_range + 1

		s = ""

		for y in range(y_min, y_max):
			for x in range(x_min, x_max):
				objs = self.terrain.get_square(x, y)

				if any([isinstance(obj, Rover) for obj in objs]):
					s += "X "

				elif any([isinstance(obj, Note) for obj in objs]):
					s += "M "

				else:
					s += "- "

			s += "\n"

		return s.rstrip()


	def drop_note(self, msg):
		note = Note(msg)
		self.terrain.add_object(note, self.x, self.y)


	def inspect_rel(self, rel_x, rel_y):
		objs = self.terrain.get_square(self.x+rel_x, self.y+rel_y)
		if not objs:
			return "Nothing to inspect."

		result = "\n".join([obj.describe() for obj in objs])
		return result
