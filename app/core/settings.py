import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URL')
    ITEMS_PER_PAGE: int = int(os.getenv('ITEMS_PER_PAGE'))

    ACCESS_TOKEN_SECRET_KEY: str = os.getenv("SECRET_KEY")
    REFRESH_TOKEN_SECRET_KEY: str = os.getenv("SUPER_SECRET_KEY")

    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    REFRESH_TOKEN_EXPIRE_MINUTES=int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))
    ALGORITHM: str = os.getenv('ALGORITHM')
    
    CACHE_TYPE: str = "RedisCache"
    CACHE_REDIS_HOST: str = os.getenv("CACHE_REDIS_HOST")
    CACHE_REDIS_PORT: int = int(os.getenv("CACHE_REDIS_PORT"))
    CACHE_REDIS_DB: int = int(os.getenv("CACHE_REDIS_DB"))
    CACHE_DEFAULT_TIMEOUT: int = int(os.getenv("CACHE_DEFAULT_TIMEOUT"))
    CACHE_REDIS_DECODE_RESPONSES: bool = os.getenv("CACHE_REDIS_DECODE_RESPONSES")

    LIMIT_PER_MINUTE: str = "5 per minute"
    LIMIT_PER_DAY: str = "1000 per day"

settings = Settings()