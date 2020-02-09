
from rover import Rover


class User:

	def __init__(self, name):
		self.name = name
		self.rover = Rover(self)