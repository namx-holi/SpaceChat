import bcrypt
from objects.rover import Rover

from config import UserConfig as userconf


class User:

	def __init__(self, username):
		self.username = username
		self.password_hash = None
		self.rover = None
		self.notes = set()
		self.smails = []
		self.session = None
		self.friends = set()


	def set_password(self, password):
		pwhash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
		self.password_hash = pwhash


	def check_password(self, password):
		return bcrypt.checkpw(password.encode(), self.password_hash)



class UserManager:

	def __init__(self):
		self.users_by_name = {}


	def create_user(self, username):
		user = User(username)
		self.users_by_name[user.username] = user

		# Give user a rover
		_ = Rover(user)

		return user


	def get_by_name(self, username):
		return self.users_by_name.get(username, None)
