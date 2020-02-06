
from terrain import Terrain
from rover import Rover

terrain = Terrain(5, 5)
rover = Rover()

terrain.add_object(rover, 3, 3)

terrain.display()
while True:
	direction = input("> ")
	rover.move(direction)
	terrain.display()
