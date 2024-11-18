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
    # SQLITE_URL: str = os.getenv("SQLITE_URL")
    RELEASE_VERSION: str = os.getenv("RELEASE_VERSION")
    SHOW_SQL_ALCHEMY_QUERIES: int = os.getenv("SHOW_SQL_ALCHEMY_QUERIES")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = os.getenv("JWT_EXPIRE_MINUTES")

    NEON_DB_USER: str = os.getenv("NEON_DB_USER") 
    NEON_DB_PASSWORD: str = os.getenv("NEON_DB_PASSWORD")  
    NEON_DB_HOST: str = os.getenv("NEON_DB_HOST") 
    NEON_DB_PORT: int = int(os.getenv("NEON_DB_PORT", 5432))  
    NEON_DB_NAME: str = os.getenv("NEON_DB_NAME") 
    NEON_DB_SSL: bool = os.getenv("NEON_DB_SSL", "True").lower() == "true"  
    

    @property
    def neon_db_url(self) -> str:
        return (
            self.NEON_DB_HOST
        )
config: Config = Config()