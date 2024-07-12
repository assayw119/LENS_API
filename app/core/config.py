from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite:///./test.db"

    # JWT settings
    SECRET_KEY: str = "ABCD1234"
    REFRESH_SECRET_KEY: str = "EFGH5678"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

class Config:
    env_file = ".env"

settings = Settings()
