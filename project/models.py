from flask_login import UserMixin
from . import db

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    caption = db.Column(db.String(250), nullable=False)
    file = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(600), nullable=True)
    

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'category'     : self.category,
           'caption'      : self.caption,
           'file'         : self.file,
           'desc'         : self.description,
       }
 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    admin = db.Column(db.Boolean, default=False) #admin column added to User table
    
