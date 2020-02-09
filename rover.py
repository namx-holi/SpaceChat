
from movable_object import MovableObject
from note import Note


class Rover(MovableObject):

	def __init__(self, user):
		super().__init__()
		self.user = user

		self.view_range = 2


	def describe(self):
		"""Describes the object when inspected.
		"""

		return f"{self.user.name}'s rover."


	def observe(self):
		"""
		Looks around the rover with it's view range and returns the
		terrain displayed as a grid.
		"""

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
		"""Leaves a note on the terrain.
		"""

		note = Note(msg)
		self.terrain.add_object(note, self.x, self.y)


	def inspect_rel(self, rel_x, rel_y):
		"""Inspects all objects in a square from the rover.
		"""

		objs = self.terrain.get_square(self.x+rel_x, self.y+rel_y)
		if not objs:
			return "Nothing to inspect."

		result = "\n".join([obj.describe() for obj in objs])
		return result
