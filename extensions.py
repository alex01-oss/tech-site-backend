from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from logs.config import setup_logging
# from flask_limiter import Limiter

# limiter = Limiter()
db = SQLAlchemy()
cache = Cache()
logger = setup_logging()