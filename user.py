
from rover import Rover


class User:

	def __init__(self, name):
		self.name = name
		self.password = None
		self.rover = Rover(self)
		self.session = None


	def set_password(self, password):
		self.password = password


	def check_password(self, password):
		if not self.password:
			return False
		return password == self.password
