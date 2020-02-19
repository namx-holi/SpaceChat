from flask import Flask
# from config import Config

from managers.message_manager import MessageManager
from managers.session_manager import SessionManager
from managers.terrain_manager import TerrainManager
from managers.user_manager import UserManager


# Init managers
session_manager = SessionManager()
terrain_manager = TerrainManager()
user_manager = UserManager()

message_manager = MessageManager(session_manager)


# def create_app(config=Config):
def create_app():
	app = Flask(__name__)
	# app.config.from_object(config)

	# init app with managers

	# Blueprint registration
	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp)
	from app.game import bp as game_bp
	app.register_blueprint(game_bp)

	return app
