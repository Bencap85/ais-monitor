from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    broadcaster_port: int = 5000

    # AWS
    aws_url: str | None = None
    aws_region_name: str = "us-east-1"
    broadcaster_queue_url: str

    base_path: str = "/broadcaster/api/v1"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()