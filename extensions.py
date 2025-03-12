from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from logs.logger import setup_logging

db = SQLAlchemy()
cache = Cache()
logger = setup_logging()