
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-12345'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///markers.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')

