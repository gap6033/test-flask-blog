# importing db from init as it is used in classes
# importing app as we need app's secret key
from flaskblog import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin


# creating a function decorator. It is to reload the user already stored in the database. @login_manager.user_loader is the decorator which allows the flask_login extension knows this is the function to get  a user by an id. @ symblo used to specify decorator
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# the flask_login extension expects your user model to have 4 attributes and methods, which is what UserMixin does.
# creating the model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # the 20 is the max characters(actually bytes, 1 byte per 1 varchar) allowed, nullable if field can be left empty or not, unique username has to be unique
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # no need for unique as we are putting default for those who don't provide image. We will hash these image files which are named 20 character long
    image_file = db.Column(db.String(20),  nullable=False, default='default.jpg')
    # we will hash password
    password = db.Column(db.String(60), nullable=False)
    # this post attribute has a relationship to the Post model below. backref equivalent to adding a column to the Post model which lets us know the user who created the post. lazy = true means SQLAlchemy will load the data from the database as necessary. This is a relationship not a column, so we wont actually see this column this would just be running as a query. P in Post is capital as we are referencing  to the entire class.
    posts = db.relationship('Post', backref='author', lazy=True)

    # repr method(magic methods). how our object is printed when ever we print it out, these are the fields which will be populated when one queries the User table
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # we dont use datetime.utcnow() as that will result in passing the outcome value as argument but we instead want to pass the function itself as the argument
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # text is used for longer text input while string for smaller ones. data type for string is varchar(variable character) and for text is text. 1 character in string takes 1 byte
    content = db.Column(db.Text, nullable=False)
    # u in user.id is lower case as we are referencing the table id in Model(class) User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
