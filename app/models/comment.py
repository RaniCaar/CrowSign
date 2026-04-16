from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    profile_id = db.Column(db.Integer, nullable=False) # ID del perfil donde se comentó
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    reactions = db.relationship('CommentReaction', backref='comment', lazy=True, cascade="all, delete-orphan")

class CommentReaction(db.Model):
    __tablename__ = 'comment_reactions'
    
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
