
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Marker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
