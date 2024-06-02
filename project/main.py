from flask import (
  Blueprint, render_template, request, 
  flash, redirect, url_for, send_from_directory, 
  current_app, make_response, session, app
)
from datetime import timedelta
from .models import Photo
from sqlalchemy import asc, text
from . import db
import os
from flask_login import login_user, login_required, logout_user, current_user


main = Blueprint('main', __name__)


@main.route('/admin')
def adminpage():
  return render_template('admin.html')


@main.route('/profile')
def profile():
  photos = db.session.query(Photo).order_by(asc(Photo.file))
  return render_template('profile.html', photos = photos)


# This is called when the home page is rendered. It fetches all images sorted by filename.
@main.route('/', methods=['GET','POST'])
def homepage():
  photos = db.session.query(Photo).order_by(asc(Photo.file))
  return render_template('index.html', photos = photos)


@main.route('/Animals', methods=['GET','POST']) # methods only included for testing purposes
def animalpage():
  photos = db.session.query(Photo).filter_by(category = "Animals") # methods only included for testing purposes
  return render_template('animals.html', photos = photos)


@main.route('/Nature', methods=['GET','POST'])
def naturepage():
  photos = db.session.query(Photo).filter_by(category = "Nature") # methods only included for testing purposes
  return render_template('nature.html', photos = photos)


@main.route('/Architecture', methods=['GET','POST'])
def architecturepage():
  photos = db.session.query(Photo).filter_by(category = "Architecture") # methods only included for testing purposes
  return render_template('architecture.html', photos = photos)


@main.route('/Other', methods=['GET','POST'])
def otherpage():
  photos = db.session.query(Photo).filter_by(category = "Other") # methods only included for testing purposes
  return render_template('other.html', photos = photos)


@main.route('/uploads/<name>')
def display_file(name):
  return send_from_directory(current_app.config["UPLOAD_DIR"], name)


@main.route('/searchresults', methods=['POST'])
def search_results():
  search = request.form.get('search')
  if "/" in search or "." in search: # prevents XSS attack by ensuring no links can be used in a search by checking for required characters in a search ensures all user input is untrusted
    return render_template('failedsearch.html') # uses a html file that takes in no variables if untrustworthy input is provided
  photos = db.session.query(Photo).filter(Photo.caption.contains(search) | Photo.name.contains(search) | Photo.category.contains(search) | Photo.description.contains(search))
  # Use of db.session.query(Photo).filter ensures that the user defined input is not used directly 
  # to make a query,instead it is used in a function that filters options and would just treat any 
  # SQL within it as the same as the rest of the string. Ensures user input is untrusted
  return render_template('search.html', photos = photos, search = search)


# Upload a new photo
@main.route('/upload/', methods=['GET','POST'])
def newPhoto():
  if request.method == 'POST':
    file = None
    if "fileToUpload" in request.files:
      file = request.files.get("fileToUpload")
    else:
      flash("Invalid request!", "error")

    if not file or not file.filename:
      flash("No file selected!", "error")
      return redirect('/upload/')

    filepath = os.path.join(current_app.config["UPLOAD_DIR"], file.filename)
    file.save(filepath)

    newPhoto = Photo(name = request.form['user'], 
                    category = request.form['category'],
                    caption = request.form['caption'],
                    description = request.form['description'],
                    file = file.filename)
    db.session.add(newPhoto)
    flash('New Photo %s Successfully Created' % newPhoto.name)
    db.session.commit()
    return redirect(url_for('main.homepage'))
  else:
    return render_template('upload.html')


# This is called when clicking on Edit. Goes to the edit page.
@main.route('/photo/<int:photo_id>/edit/', methods = ['GET', 'POST'])
def editPhoto(photo_id):
  editedPhoto = db.session.query(Photo).filter_by(id = photo_id).one()
  if editedPhoto.name != current_user.name and not current_user.admin: #control access
    flash('Photo %s cannot be edited' % editedPhoto.name)
    return redirect(url_for('main.homepage'))
  if request.method == 'POST':
    if request.form['user']:
      editedPhoto.name = request.form['user']
      editedPhoto.category = request.form['category']
      editedPhoto.caption = request.form['caption']
      editedPhoto.description = request.form['description']
      db.session.add(editedPhoto)
      db.session.commit()
      flash('Photo Successfully Edited %s' % editedPhoto.name)
      return redirect(url_for('main.homepage'))
  else:
    return render_template('edit.html', photo = editedPhoto)

# This is called when clicking on Delete.


@main.route('/photo/<int:photo_id>/delete/', methods = ['GET','POST'])
def deletePhoto(photo_id):
  photo = db.session.query(Photo).filter_by(id = photo_id).one() # Control access
  if photo.name != current_user.name and not current_user.admin:
    flash('Photo %s cannot be deleted' % photo.name)
    return redirect(url_for('main.homepage'))
  fileResults = db.session.execute(text('select file from photo where id = %s', str(photo_id)))
  filename = fileResults.first()[0]
  filepath = os.path.join(current_app.config["UPLOAD_DIR"], filename)
  os.unlink(filepath)
  db.session.execute(text('delete from photo where id = %s', str(photo_id)))
  db.session.commit()
  
  flash('Photo id %s Successfully Deleted' % photo_id)
  return redirect(url_for('main.homepage'))

