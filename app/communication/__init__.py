from flask import Blueprint
bp = Blueprint("communication", __name__)
from app.communication import endpoints
