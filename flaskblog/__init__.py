import os
from flask import Flask
# flask specific SQLAlchemy library there is a general python one as well. SQLAlchemy is an ORM i.e. allows us to transition from one form of database to another eg from sqlite to postgresql without the need for making changes to the code. You won't have to rewrite all your database code. The tradeoff is the loss of backend-specific features, since the abstraction can only abstract the operations and capabilities common to all the backends without losing the portability advantage.
# SQLAlchemy allows us to create db structures(the tables) as classes (called as models)
from flask_sqlalchemy import SQLAlchemy

#for password authentication
from flask_bcrypt import Bcrypt
# for Login
from flask_login import LoginManager
from flask_mail import Mail



app = Flask(__name__)

# this key is necessary to prevent CSRF(cross-site request forgery) attacks.
# Generated with method secrets.token_hex(16) of secrets class. The 16 is the number of bytes allocated for total output. Hexadecimal character is of 4 bits, thus, each byte represents two Hexadecimal character below.
app.config['SECRET_KEY'] ='5e676a7d5a75cee822e327aad12d1772'
# sets the location for storing the sqlite db named site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# create db instance
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# this will lead the user to login page if he tries to access the account page through the url bar without login into the website. It automatically displays "Please log in to access this page."
login_manager.login_view='login'
# Please log in to access this page text is styled
login_manager.login_message_category = 'info'



# to avoid circular error "cannot import name 'app' from 'flaskblog' as called in routes file
from flaskblog import routes
