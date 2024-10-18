import boto3
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    UNIVERSAL_SECRET: str
    ALGORITHM: str
    
    class Config:
        env_file = ".env"


def fetch_secrets():
    secret_id = "organization/branch/secret"
    client = boto3.client("secretsmanager", region_name="ap-south-1")
    response = client.get_secret_value(SecretId=secret_id)
    secret_string = response["SecretString"]
    return secret_string


def load_settings_from_secrets():
    secret_string = fetch_secrets()
    settings = Settings.parse_raw(secret_string)
    return settings


# settings = load_settings_from_secrets()
settings = Settings()