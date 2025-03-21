import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        image_file = form.upload.data
        filename = secure_filename(image_file.filename)
        uploads = app.config['UPLOAD_FOLDER']
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        path = os.path.normpath(os.path.join(uploads, filename))
        try:
            image_file.save(path)
            flash('File Saved', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(f"An error occurred while saving the file: {str(e)}", 'danger')
        # image_file.save(path)
        # flash('File Saved', 'success')
        # return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template('upload.html', form=form)

@app.route('/uploads/<filename>')
def get_image(filename):
    print(f"Serving file from: {app.config['UPLOAD_FOLDER']}, Filename: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files')
@login_required
def files():
    image_list = get_uploaded_images()
    return render_template('files.html', images=image_list)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = UserProfile.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful','success')
            return redirect(url_for('upload'))
        else:
            flash('Incorrect username or password, please try again','danger')
    return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful','info')
    return redirect(url_for('home'))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

def get_uploaded_images():
    uploads = app.config['UPLOAD_FOLDER']
    images = []
    tru_img = ['jpg', 'png']
    for subdir, dirs, files in os.walk(uploads):
        for file in files:
            if file.split('.')[-1].lower() in tru_img:
                images.append(file)
    return images