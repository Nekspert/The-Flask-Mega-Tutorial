import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))


class Config:
    load_dotenv(os.path.join(basedir, ".env"))

    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess21_01_25"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, "app.db")

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") or not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = ["your-email@example.com"]

    POSTS_PER_PAGE = 10

    LANGUAGES = ["en", "ru"]

    WHOOSH_INDEX_DIR = os.environ.get("WHOOSH_INDEX_DIR")

    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
