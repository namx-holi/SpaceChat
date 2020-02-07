
class UserInterface:

	def __init__(self, rover):
		self.rover = rover

		self.commands = {
			"move": self.move,
			"observe": self.observe,
			"exit": self.exit,
		}

		self.querying = False


	def query_loop(self):
		self.querying = True
		while self.querying:
			self.query_action()


	def query_action(self):
		action = input("> ")

		# Ignore empty imput
		if action is "":
			return

		command, _, args = action.partition(" ")
		if command not in self.commands:
			# TODO: Error
			print(f"{action} not valid action")
			return

		if args:
			args = args.split(" ")
		else:
			args = []
		return self.commands[command](args)


	def move(self, args):
		if len(args) != 1:
			print("Wrong number of arguments")
			return

		direction = args[0].lower()
		if direction in ["n", "north"]:
			self.rover.move_rel(0, -1)

		elif direction in ["e", "east"]:
			self.rover.move_rel(+1, 0)

		elif direction in ["s", "south"]:
			self.rover.move_rel(0, +1)

		elif direction in ["w", "west"]:
			self.rover.move_rel(-1, 0)

		else:
			print("Invalid direction")
			return


	def observe(self, args):
		if len(args) != 0:
			print("Wrong number of arguments")
			return

		self.rover.terrain.display()


	def exit(self, args):
		if len(args) != 0:
			print("Wrong number of arguments")

		self.querying = False
		print("Exiting!")
