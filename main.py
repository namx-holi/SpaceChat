
from terrain import Terrain
from rover import Rover
from user_interface import UserInterface

terrain = Terrain(5, 5)

start_x, start_y = 3, 3
rover = Rover(terrain, start_x, start_y)
terrain.display()

user_interface = UserInterface(rover)
user_interface.query_loop()
