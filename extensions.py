from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
cors = CORS()
jwt = JWTManager()
f_bcrypt = Bcrypt()
