from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_UNIVERSAL_SECRET: str
    REALTIME_TRACKING_SECRET: str
    ALGORITHM: str
    SQS_QUEUE_URL: str
    SQS_NOTIFICATION_QUEUE_URL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    AUTH_SERVICE_URL: str   # localhost:8000/
    LOCATION_SERVICE_URL: str   # localhost:8004/
    
    class Config:
        env_file = ".env"

settings = Settings()