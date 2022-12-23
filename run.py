# we need to import app to run app in app.run, this instance of app has to exist in init.py. The flaskblog here refers to the package
from flaskblog import app

if __name__=='__main__':
    app.run(debug=True)
