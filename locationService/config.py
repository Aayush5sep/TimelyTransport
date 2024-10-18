from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    AUTH_SERVICE_URL: str
    AUTH_UNIVERSAL_SECRET: str
    REALTIME_TRACKING_SECRET: str
    ALGORITHM: str
    
    class Config:
        env_file = ".env"

settings = Settings()