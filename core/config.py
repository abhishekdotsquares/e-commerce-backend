import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class BaseConfig(BaseSettings):
    class Config:
        case_sensitive = True

class Config(BaseConfig):
    DEBUG: int = os.getenv("DEBUG")
    DEFAULT_LOCALE: str = os.getenv("DEFAULT_LOCALE")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    SQLITE_URL: str = os.getenv("SQLITE_URL")
    RELEASE_VERSION: str = os.getenv("RELEASE_VERSION")
    SHOW_SQL_ALCHEMY_QUERIES: int = os.getenv("SHOW_SQL_ALCHEMY_QUERIES")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = os.getenv("JWT_EXPIRE_MINUTES")

config: Config = Config()