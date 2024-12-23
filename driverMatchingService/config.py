from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str
    AUTH_UNIVERSAL_SECRET: str
    ALGORITHM: str
    SQS_NOTIFICATION_QUEUE_URL: str
    LOCATION_SERVICE_URL: str
    TRIP_MANAGEMENT_SERVICE_URL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()