import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = os.getenv('DATABASE_URL')
    ITEMS_PER_PAGE: int = int(os.getenv('ITEMS_PER_PAGE', '10'))

    ACCESS_TOKEN_SECRET_KEY: str = os.getenv("SECRET_KEY", "mysecretaccesskey")
    REFRESH_TOKEN_SECRET_KEY: str = os.getenv("SUPER_SECRET_KEY", "mysecretrefreshkey")

    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    REFRESH_TOKEN_EXPIRE_MINUTES=int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', '43200'))
    ALGORITHM: str = os.getenv('ALGORITHM', 'HS256')
    
    CACHE_TYPE: str = "RedisCache"
    CACHE_REDIS_HOST: str = os.getenv("CACHE_REDIS_HOST", "localhost")
    CACHE_REDIS_PORT: int = int(os.getenv("CACHE_REDIS_PORT", 6379))
    CACHE_REDIS_DB: int = int(os.getenv("CACHE_REDIS_DB", 0))
    CACHE_DEFAULT_TIMEOUT: int = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))

    LIMIT_PER_MINUTE: str = "5 per minute"
    LIMIT_PER_DAY: str = "1000 per day"

settings = Settings()