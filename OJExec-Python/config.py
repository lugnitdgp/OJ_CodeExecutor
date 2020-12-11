import os
from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))

enginedir = os.path.abspath(os.path.join(basedir, "safeexec"))

engine_path = os.path.join(enginedir, "safeexec")

staticdir = os.path.abspath(os.path.join(basedir, "static"))


class Config(object):
    DEBUG = config("DEBUG", cast=bool)
    TESTING = True
    CSRF_ENABLED = True
    SECRET_KEY = config("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
