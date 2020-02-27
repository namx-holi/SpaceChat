from app.models import User, Rover

from config import UserConfig as userconf


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
