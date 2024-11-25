class Config:
    # Database
    NEON_DB_HOST = "postgresql+asyncpg://harmannstudios_owner:OCE4JHxpzl8h@ep-square-dew-a5ke67mm.us-east-2.aws.neon.tech/dev_harmannstudios"
    neon_db_url = "postgresql+asyncpg://harmannstudios_owner:OCE4JHxpzl8h@ep-square-dew-a5ke67mm.us-east-2.aws.neon.tech/dev_harmannstudios"
    NEON_DB_PORT = 5432
    NEON_DB_NAME = "dev_harmannstudios"
    NEON_DB_USER = "abhishek.tripathi@dotsquares.com"
    NEON_DB_PASSWORD = "aBHItRI@22"
    NEON_DB_SSL = True

    # SQLITE_URL = "sqlite+aiosqlite:///./user.db"
    # TEST_SQLITE_URL = "sqlite+aiosqlite:///./test_user.db"
    SECRET_KEY = "5bf63208bcee104f43c7da74e784f1193ab60d8c2d095175538b5546a835b940"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 1440
    DEFAULT_LOCALE = "en_US"
    RELEASE_VERSION = "0.1"
    SHOW_SQL_ALCHEMY_QUERIES = 0
    DEBUG = 1

    # Environment
    ENVIRONMENT = "development"


# Instantiate the Config class to make it accessible
config = Config()
