import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CACHE_TYPE = os.getenv('CACHE_TYPE')
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', '10'))
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
