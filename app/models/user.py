from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    identity = db.Column(db.String(50), nullable=True) # Mujer, Hombre, No binario
    age = db.Column(db.Integer, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(255), default='default_avatar.png')
    banner_pic = db.Column(db.String(255), default='default_banner.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    comments = db.relationship('Comment', backref='user', lazy=True)
    
class Follower(db.Model):
    __tablename__ = 'followers'
    
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
