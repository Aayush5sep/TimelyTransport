from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQS_QUEUE_NAME: str
    AUTH_UNIVERSAL_SECRET: str
    ALGORITHM: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_ACCESS_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()