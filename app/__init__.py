from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate
import redis
from flask_login import LoginManager

from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
# db = redis.Redis()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
from app import routes