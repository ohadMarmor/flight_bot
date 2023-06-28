from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from database import db


class User(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(50))


class Conversation(db.Model):
    conversation_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('user.email'))
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all,delete')
    flight_profile = db.relationship('FlightProfile', backref='conversation', uselist=False, lazy=True)


class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    is_user = db.Column(db.Boolean)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.conversation_id'))


class FlightProfile(db.Model):
    flight_profile_id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.conversation_id'))
    date_from = db.Column(db.String(50), default='anytime')
    date_until = db.Column(db.String(50), default='anytime')
    num_of_passengers = db.Column(db.Integer, default=-1)
    destination_str = db.Column(db.String(200), default=None)
    sports_str = db.Column(db.String(200), default=None)
    weather_str = db.Column(db.String(200), default=None)
    activities_str = db.Column(db.String(200), default=None)
    food_str = db.Column(db.String(200), default=None)
    teams_str = db.Column(db.String(200), default=None)

    @property
    def preferences(self):
        return {
            "destinations": self._deserialize_str(self.destination_str),
            "sports": self._deserialize_str(self.sports_str),
            "weather": self._deserialize_str(self.weather_str),
            "activities": self._deserialize_str(self.activities_str),
            "food": self._deserialize_str(self.food_str),
            "teams": self._deserialize_str(self.teams_str)
        }

    @preferences.setter
    def preferences(self, new_preferences):
        self.destination_str = self._serialize_str(new_preferences.get("destinations", []))
        self.sports_str = self._serialize_str(new_preferences.get("sports", []))
        self.weather_str = self._serialize_str(new_preferences.get("weather", []))
        self.activities_str = self._serialize_str(new_preferences.get("activities", []))
        self.food_str = self._serialize_str(new_preferences.get("food", []))
        self.sports_str = self._serialize_str(new_preferences.get("teams", []))

    @staticmethod
    def _serialize_str(lst):
        return ",".join(lst)

    @staticmethod
    def _deserialize_str(string):
        return string.split(",") if string else []
