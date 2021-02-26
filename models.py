#Imports

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
# TODO: connect to a local postgresql database
app.config.from_object('config')
db = SQLAlchemy(app)
migrate=Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Show model
class Show(db.Model):
  __tablename__= 'Show'

  artist_id= db.Column(db.Integer, db.ForeignKey('Artist.id'),primary_key= True)
  venue_id= db.Column(db.Integer, db.ForeignKey('Venue.id'),primary_key= True)
  start_time= db.Column(db.DateTime,nullable=False)
  
  def __repr__(self):
    return f'<Show {self.artist_id} {self.venue_id} {self.start_time}>'

# Venue model
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    genres=db.Column(db.String,nullable=False)
    address = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    website=db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String)
    image_link = db.Column(db.String(500))
    Artists= db.relationship('Artist', secondary=lambda: Show.__table__, backref='venue', lazy= True)

# Artist model
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False,unique=True)
    genres=db.Column(db.String,nullable=False)
    address = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    website=db.Column(db.String)
    facebook_link = db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String)
    image_link = db.Column(db.String(500))

