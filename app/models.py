# from app import db
import bcrypt



class User:

	def __init__(self, username):
		self.username = username
		self.password_hash = None
		self.rover = None
		self.notes = set()
		self.smails = []


	def set_password(self, password):
		pwhash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
		self.password_hash = pwhash


	def check_password(self, password):
		return bcrypt.checkpw(password.encode(), self.password_hash)



class SMail:
	def __init__(self, sender, recipient, subject, msg):
		self.sender = sender
		self.recipient = recipient

		# TODO: Add ref in recipient to this
		# self.recipient.smails.append(self)

		self.subject = subject
		self.msg = msg



class Object:

	PRIORITY=0
	CHARACTER="?"

	@property
	def terrain(self):
		if self.tile:
			return self.tile.terrain
		return None

	@property
	def x(self):
		if self.tile:
			return self.tile.x
		return None

	@property
	def y(self):
		if self.tile:
			return self.tile.y
		return None

	def __init__(self):#, char, prio):
		# self.PRIORITY = prio
		# self.CHARACTER = char
		self.tile = None

	def describe(self):
		return "A generic object."

	# TODO: Move to terrain manager
	def move_rel(self, delta_x, delta_y):
		if not self.tile:
			raise Exception("tried to move object not on terrain")
		new_x = self.x + delta_x
		new_y = self.y + delta_y

		# Save terrain to reference later
		terrain = self.tile.terrain
		self.tile.remove_object(self)
		terrain.get_tile(new_x, new_y).add_object(self)



class Rover(Object):

	PRIORITY=100
	CHARACTER="R"

	def __init__(self, user):
		super().__init__()

		# Bind to user and make backref
		self.user = user
		user.rover = self

		# Number of tiles distance the rover can observe
		self.view_range = 2


	def describe(self):
		return f"{self.user.username}'s rover."


	# TODO: Move to endpoint logic
	def observe(self):
		# +1 for range because range works like [start, end)
		x_min = self.x - self.view_range
		x_max = self.x + self.view_range + 1
		y_min = self.y - self.view_range
		y_max = self.y + self.view_range + 1

		tile_characters = []
		for y in range(y_min, y_max):
			row = []
			for x in range(x_min, x_max):
				tile = self.tile.terrain.get_tile(x,y)
				row.append(tile.as_character())
			tile_characters.append(row)

		return tile_characters


	# TODO: Move to endpoint logic
	def leave_note(self, msg):
		# We don't need to use the returned Note as
		# on initialisation, it adds itself to the
		# tile this rover is on!
		_ = Note(self.user, msg)



class Note(Object):

	PRIORITY=50
	CHARACTER="M"

	def __init__(self, user, msg):
		super().__init__()

		# Bind to user and make backref
		self.user = user
		user.notes.add(self)

		# Add content
		self.msg = msg

		# Add to terrain of users rover
		user.rover.tile.add_object(self)


	def describe(self):
		return f"{self.user.username}'s note. It says '{self.msg}'"
