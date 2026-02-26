from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_NAME: str
    REDIS_URL: str
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
    )
    
settings = Setting()


