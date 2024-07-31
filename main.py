from flask import Flask
from flask_cors import CORS 
import sys



app = Flask(__name__, static_folder="frontend/static")   # Specify where static folder is (relative to this file)

# Frontend client needs to fetch json data from the backend server. This is normally forbidden by the Same-Origin policy since loading external data should not be trusted. This line of code overrides that.
CORS(app) 


#The imports are very confusing, but these two need to be here for everything to work
import backend.utils as utils 
from backend.routes import main




# Necessary because Gunicorn can't handle cmd arguments
def create_app(admin_user:str, fresh_db:bool):
    main(admin_user, fresh_db)        # Located in backend/routes.py
    return app

#This is only used when not running app with Gunicorn (i.e. debug)
if __name__ == "__main__":
    create_app(sys.argv[1], bool(int(sys.argv[2])))


