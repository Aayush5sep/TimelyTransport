from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQS_QUEUE_URL: str
    AUTH_UNIVERSAL_SECRET: str
    ALGORITHM: str
    
    class Config:
        env_file = ".env"

settings = Settings()