from flask import Flask 
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from decouple import config

app = Flask(__name__)
app.config["CELERY_BROKER_URL"] = config("CELERY_BROKER_URL")
app.config["CELERY_RESULT_BACKEND"] = config("CELERY_RESULT_BACKEND")

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

celery = Celery(app.name(), broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from app import views, models