
class UserInterface:

	def __init__(self, rover):
		self.rover = rover

		self.commands = {
			"move": self.move,
			"observe": self.observe,

			"note": self.note,
			"inspect": self.inspect,

			"exit": self.exit,
		}

		self.querying = False


	def query_loop(self):
		self.querying = True
		while self.querying:
			action = input("> ")
			self.parse_action(action)


	def parse_action(self, action):
		# Ignore empty imput
		if action is "":
			return

		action = action.strip()
		command, _, args = action.partition(" ")
		if command not in self.commands:
			# TODO: Error
			return f"{action} not valid action"

		if args:
			args = args.split(" ")
		else:
			args = []

		return self.commands[command](args)


	def move(self, args):
		if len(args) != 1:
			return "Wrong number of arguments"

		# TODO: Make function to parse direction easily
		direction = args[0].lower()
		if direction in ["n", "north"]:
			self.rover.move_rel(0, -1)
			return "Moved North"

		elif direction in ["e", "east"]:
			self.rover.move_rel(+1, 0)
			return "Moved East"

		elif direction in ["s", "south"]:
			self.rover.move_rel(0, +1)
			return "Moved South"

		elif direction in ["w", "west"]:
			self.rover.move_rel(-1, 0)
			return "Moved West"

		else:
			return "Invalid direction"


	def observe(self, args):
		if len(args) != 0:
			return "Wrong number of arguments"

		grid_s = self.rover.observe()
		return grid_s


	def exit(self, args):
		if len(args) != 0:
			return "Wrong number of arguments"

		self.querying = False
		return "Exiting!"


	def note(self, args):
		if len(args) <= 0:
			return "Wrong number of arguments"

		msg = " ".join(args)
		self.rover.drop_note(msg)
		return "Note added"


	def inspect(self, args):
		if len(args) != 1:
			return "Wrong number of arguments"

		# TODO: Make function to parse direction easily
		direction = args[0].lower()
		if direction in ["n", "north"]:
			return self.rover.inspect_rel(0, -1)

		elif direction in ["e", "east"]:
			return self.rover.inspect_rel(+1, 0)

		elif direction in ["s", "south"]:
			return self.rover.inspect_rel(0, +1)

		elif direction in ["w", "west"]:
			return self.rover.inspect_rel(-1, 0)

		else:
			return "Invalid direction"
