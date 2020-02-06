
from terrain import Terrain
from rover import Rover

terrain = Terrain(5, 5)
rover = Rover()

terrain.add_object(rover, 3, 3)

terrain.display()
while True:
	inp = input("> ")

	if inp is "":
		pass

	elif inp in ["o", "observe"]:
		terrain.display()

	elif inp in ["exit", "quit"]:
		break

	else:
		rover.move(inp)
