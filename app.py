#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify ,abort
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import sys
from wtforms import ValidationError
import phonenumbers
from models import *
from forms import *



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

def phone_validator(num):
  phone= phonenumbers.parse(num, "US")
  if not phonenumbers.is_valid_number(phone):
    raise ValidationError('Must be a valid US phone number.')

def name_validator_unique(model_name,field_value):
  valueOfField=field_value.lower()

  print(valueOfField)
  all_rows=model_name.query.all()
  for row in all_rows:
    name_value=row.name.lower()
    if(name_value==valueOfField):
      raise ValidationError('The name is already existed.')

  '''check=model_name.query.filter_by(name=value).first()
  print('//////////////////////////////////////////////')
  print(value)
  if(check):
    raise ValidationError('The name is already existed.')'''

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  venues_cities_states = set()
  for v in venues:
    # add tuples that contain city&state
    venues_cities_states.add((v.city, v.state))

  for position in venues_cities_states:
    data.append({
    "city": position[0],
    "state":position[1],
    "venues": []
  })

  # get number of upcoming shows for each venue
  for venue in venues:
    numOfUpcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()

    # comparing the time of now with the start time
    
    for s in shows:
      if s.start_time > datetime.now():
        numOfUpcoming_shows += 1

    # for each entry, add venues to matching city/state
    for item in data:
      if venue.city == item['city'] and venue.state == item['state']:
            
        item['venues'].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": numOfUpcoming_shows
        })

  #return venues page 
  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(venues),
    "data": []
  }

  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()

    # calculuate num of upcoming shows
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.filter_by(id=venue_id).first()

  # get all shows for given venue
  shows = Show.query.filter_by(venue_id=venue_id).all()
  # returns upcoming shows
  def shows_upcoming():
    #upcoming = []
    upcoming_shows = []
    upcoming_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()  
    for show,artist in upcoming_shows_query:
      upcoming_shows.append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link": artist.image_link,
        "start_time":format_datetime(str(show.start_time))

      }) 
    return upcoming_shows

  

  # returns past shows
  def shows_past():
    #past = []
    past_shows=[]
    past_shows_query = db.session.query(Show,Artist).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time<datetime.now()).all()  
    for show,artist in past_shows_query:
      past_shows.append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link": artist.image_link,
        "start_time":format_datetime(str(show.start_time))

      }) 
    return past_shows
  

  # data for given venue
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": shows_past(),
    "upcoming_shows":shows_upcoming(),
    "past_shows_count": len(shows_past()),
    "upcoming_shows_count": len(shows_upcoming())
  }

  # return venue data
  return render_template('pages/show_venue.html', venue=data)
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  #form=VenueForm()
  #if form.validate_on_submit():
  #error=False
  try:
    
    name = request.form.get('name')
    name_validator_unique(Venue,name)
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    phone_validator(phone)
    image = request.form.get('image_link')
    facebook = request.form.get('facebook_link') 
    seeking = int(request.form.get('seeking_talent'))
    seekingDesc = request.form.get('seeking_description')
    genres = request.form.get('genres')
    website = request.form.get('website')
    
    
    venue = Venue(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook,genres=genres,
    image_link=image,seeking_talent=bool(seeking),seeking_description=seekingDesc,website=website)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  except ValidationError as e:
    db.session.rollback()
    flash('There is an error occurred in the name field ' +
    request.form.get('name') + ' could not be listed. ' + str(e))


  except ValidationError as e:
    db.session.rollback()
    flash('There is an error occurred. Venue ' +
    request.form.get('name') + ' could not be listed. ' + str(e))
    #error=True
  except:
    db.session.rollback()
    #error=True
    flash('There is an error occurred. Venue ' +
    request.form.get('name') + ' could not be listed. ' )
    print(sys.exc_info())
  finally:
    db.session.close()
  """if error:
    print("Errooooooooooooooooooooor")
    #abort (400)
    flash('There is an error occurred. Venue ' +
    request.form.get('name') + ' could not be listed. ' )"""
  
  """else:
    print("WOOOHOOO venue successfully added")"""

    # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

  #else:
    #flash('Venue ' + request.form['name'] + ' does not successfully listed!')
    #return render_template('forms/new_venue.html')
    #return "venue error"

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists=Artist.query.all()
  for artist in artists:
    data.append({
      "id":artist.id,
      "name":artist.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists= Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response = {
    "count": len(artists),
    "data": []
  }

  for artist in artists:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(artist_id=artist.id).all()

    # calculuate num of upcoming shows
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    })
 

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist=Artist.query.filter_by(id=artist_id).first()

  # find all shows of this artist
  shows=Show.query.filter_by(artist_id=artist_id).all()

  #find upcomming shows
  def shows_upcoming():
    #upcomming=[]
    upcoming_shows = []
    upcoming_shows_query = db.session.query(Show,Venue).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()  
    for show,venue in upcoming_shows_query:
      upcoming_shows.append({
        "venue_id":show.venue_id,
        "venue_name":venue.name,
        "venue_image_link": venue.image_link,
        "start_time":format_datetime(str(show.start_time))

      }) 
    '''for show in shows:
      if show.start_time > datetime.now() :
        upcomming.append({
          "venue_id":show.venue_id,
          "venue_name":Venue.query.filter_by(id=show.venue_id).first().name,
          "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
          "start_time": format_datetime(str(show.start_time))
        })'''
    return upcoming_shows
  # find past shows
  def shows_past():
    #past=[]
    past_shows = []
    past_shows_query = db.session.query(Show,Venue).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
    print(past_shows_query)
    for show,venue in past_shows_query:
      past_shows.append({
        "venue_id":show.venue_id,
        "venue_name":venue.name,
        "venue_image_link": venue.image_link,
        "start_time":format_datetime(str(show.start_time))

      })
    '''for show in shows:
      if show.start_time < datetime.now() :
        past.append({
          "venue_id":show.venue_id,
          "venue_name":Venue.query.filter_by(id=show.venue_id).first().name,
          "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
          "start_time": format_datetime(str(show.start_time))
        })'''
    return past_shows
  # data of the artist
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "address":artist.address,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": shows_past(),
    "upcoming_shows": shows_upcoming(),
    "past_shows_count": len(shows_past()),
    "upcoming_shows_count": len(shows_upcoming()),
    }

  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form= ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #form=ArtistForm()
  #if form.validate_on_submit():
  try:
    name = request.form.get('name')
    name_validator_unique(Artist,name)
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    phone_validator(phone)
    image = request.form.get('image_link')
    facebook = request.form.get('facebook_link')
    seeking =int(request.form.get('seeking_venue')) 
    seekingDesc = request.form.get('seeking_description')
    genres = request.form.get('genres')
    website = request.form.get('website')
    
    artist=Artist(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook,genres=genres,
    seeking_venue=bool(seeking),image_link=image,seeking_description=seekingDesc,website=website)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  except ValidationError as e:
    db.session.rollback()
    flash('There is an error occurred in the name field ' +
    request.form.get('name') + ' could not be listed. ' + str(e))

  except ValidationError as e:
    db.session.rollback()
    flash('There is an error occurred. Artist ' +
    request.form.get('name') + ' could not be listed. ' + str(e))
    #error=True
  except:
    db.session.rollback()
    #error=True
    flash('There is an error occurred. Artist ' +
    request.form.get('name') + ' could not be listed. ' )
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')
  

    



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows=Show.query.all()
  for show in shows:
    data.append({
      "venue_id":show.venue_id,
      "artist_id":show.artist_id,
      'artist_name':Artist.query.filter_by(id=show.artist_id).first().name,
      'venue_name':Venue.query.filter_by(id=show.venue_id).first().name,
      'artist_image_link':Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": format_datetime(str(show.start_time))

    })
    #"venue_id": 3,
    #"venue_name": "Park Square Live Music & Coffee",
    #"artist_id": 6,
    #"artist_name": "The Wild Sax Band",
    #"artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #"start_time": "2035-04-15T20:00:00.000Z"
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error=False
  #form=ShowForm()
  #if form.validate_on_submit():
  Artist_id = request.form.get('artist_id')
  Venue_id = request.form.get('venue_id')
  Start_time= request.form.get('start_time')

  try:
      show=Show(artist_id=Artist_id,venue_id=Venue_id,start_time=Start_time)
      db.session.add(show)
      db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    print("Errooooooooooooooooooooor")
    abort (400)
  else:
    print("WOOOHOOO show successfully added")
    # on successful db insert, flash success
    flash('Show was successfully listed!')


  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
