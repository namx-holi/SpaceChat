import struct


class AppConfig:
	...


class MessageConfig:
	MSG_LEN_CHAR = "I" # Represents an int
	MSG_LEN_BYTES = struct.calcsize(MSG_LEN_CHAR)

	HOST = "0.0.0.0"
	PORT = 7778

	MSG_CHECK_TIMEOUT = 0.25


class SessionConfig:
	INACTIVITY_TIMEOUT_TIME = 30 # Minutes


class TerrainConfig:
	...


class UserConfig:
	...