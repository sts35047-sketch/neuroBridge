from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Hospital Table
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))

# Donor Table
class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    organ = db.Column(db.String(50), nullable=False, index=True)
    city = db.Column(db.String(50), index=True)
    phone = db.Column(db.String(20), unique=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), index=True)

# Recipient Table
class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    blood_group = db.Column(db.String(10), nullable=False, index=True)
    organ = db.Column(db.String(50), nullable=False, index=True)
    urgency = db.Column(db.String(20), index=True) # High, Medium, Low
    city = db.Column(db.String(50), index=True)
    phone = db.Column(db.String(20), unique=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), index=True)

# Notification Table
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), index=True)
    message = db.Column(db.String(500), nullable=False)
    date = db.Column(db.String(50), default=datetime.now().strftime("%d %b %Y, %H:%M"))
    is_read = db.Column(db.Boolean, default=False, index=True)

# Activity Log Table
class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), index=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)
    
    def format_time(self):
        return self.timestamp.strftime("%d %b, %I:%M %p")

# NEW: Message Table
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    subject = db.Column(db.String(100))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)

    def format_time(self):
        return self.timestamp.strftime("%d %b, %H:%M")