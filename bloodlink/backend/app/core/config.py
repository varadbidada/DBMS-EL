from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    MONGO_INITDB_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    MONGO_INITDB_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    MONGO_HOST: str = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT: str = os.getenv("MONGO_PORT", "27017")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "changeme")

    model_config = SettingsConfigDict(env_file="../../.env", env_file_encoding="utf-8")

settings = Settings()
