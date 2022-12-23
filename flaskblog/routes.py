# this app is for @app.
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
# notice the change from models to flaskblog.models to refer to module inside the package
from flaskblog.models import User, Post
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
# to save file uploaded to the database in the same format as it was
import os
# Pillow library to reduce the pixel size of profile picture uploaded, the largest image on the site in our CSS is set to 125 pixels, thus no use in having a larger pixel scalled down; slows down the website transmitting large file, takes unnecessary space
from PIL import Image
from flask_mail import Message

@app.route('/')
@app.route('/index')
def index():
    # query all the posts from the database
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', posts = posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET','POST'])
def register():
    # if user is already logged in take him to the home/index page
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id = current_user.id))
    form = RegistrationForm()
    # to check if the form was validated when it was submitted
    if form.validate_on_submit():
        # if registration successfull then hash password and convert the hashed password into utf-8 format
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # storing the data into the User table of the site database
        user = User(username=form.username.data, email=form.email.data,
        password=hashed_password)
        db.session.add(user)
        db.session.commit()
        # flashes message on succesful submission
        flash(f'You have now successfully registered an account!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    # if user is already logged in take him to the home/index page
    if current_user.is_authenticated:
        return redirect(url_for('user', user_id = current_user.id))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # to log them in using flask_login extension
            login_user(user, remember=form.remember.data)
            # for being directed to account page on logging in rather than home page when one tries to access the account page without logging in.
            # args is a dictionary but we don't use square bracket(will give error if next key is not present) to access the value and use get(will return none if next is not present) method
            # if one tries to access account page without logging in he will see url : http://127.0.0.1:5000/login?next=%2Faccount, here %2F amounts to '/', so below we are basically fetching the value of next if it exists(which will be '/account')
            next_page = request.args.get('next')
            # a turnary conditional
            # redirected to account page if next exists else to the home page.
            return redirect(next_page) if next_page else redirect(url_for('user', user_id = current_user.id))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title = 'Login', form=form)

@app.route('/logout')
def logout():
    # to logout from page
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_picture):
    # changing the original filename into random 8 character name
    random_hex = secrets.token_hex(8)
    # using _ as a throw away variable name, a python convention, os.path.splitext(path)
    # Split the pathname path into a pair (root, ext) such that root + ext == path, and ext is empty or begins with a period and contains at most one period. Leading periods on the basename are ignored; splitext('.cshrc') returns ('.cshrc', '').
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # app.root_path wil give the root path of our application on aur system all the way to the package directory(flaskblog package)
    # we are actually saving the file inside the same folder(profile_pictures) but just the name has changed due to picture_fn
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_fn)
    # changing pixel size, its a tuple
    output_size = (125, 125)
    # Image.open()from PILLOW(aka PIL) library, Image is the module, open is the method
    i = Image.open(form_picture)
    # .thumbnail method from PIL
    i.thumbnail(output_size)
    # saving the picture at the path we created
    i.save(picture_path)
    # ensures something is returned from function in this case the new file name
    return picture_fn

@app.route('/edit_profile', methods=['GET', 'POST'])
# to ensure that a person has access only once he has successfully logged in. only then he will have access to this route.
@login_required
def edit_profile():
    form = UpdateAccountForm()
    # updating the data in db if account information succesfully updated
    if form.validate_on_submit():
        # if picture data posted through the account update form
        if form.picture.data:
            # create a new variable to store the return value generated through save_picture function defined above
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Profile Information Updated!", 'success')
        return redirect(url_for('edit_profile'))
    # to populate current username and email in the boxes account page
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # current_user.image_file defined in modles.db with default value as default.jpg, when we update the picture current_user.image_file value gets automatically updated through the if form.picture.data condition.
    image_file = url_for('static', filename = 'profile_pictures/'+ current_user.image_file)
    return render_template('edit_profile.html', title='Edit Profile', form=form, image_file=image_file)

@app.route('/post/new', methods=['GET', 'POST'])
# can only post if user logged in
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # if the post is sucessfully made create variable post and update title, content, author(backref) field of the POST database as defined in models.py
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('user', user_id = current_user.id))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

# routing to a specific post through post id, int as post_id will be an integer, id of a post is part of route, within angular bracket is a variable
@app.route('/post/<int:post_id>')
def post(post_id):
    # get the post or return 404 error
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post )

@app.route('/user/<int:user_id>')
def user(user_id):
    page = request.args.get('page', 1, type=int)
    # get the post or return 404 error
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user.html', title=user.username, posts=posts, user=user)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Manually aborting. 403 response is http response for forbidden route
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # we don't need db.session.add as the data is already there and we are just updating it
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
        # else populate the form with the old data itself
    elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Manually aborting. 403 response is http response for forbidden route
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('user', user_id = current_user.id))
