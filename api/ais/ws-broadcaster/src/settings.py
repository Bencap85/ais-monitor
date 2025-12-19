from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    broadcaster_port: int = 5000
    
    # Database
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432

    # Connection pool
    pg_minconn: int = 1
    pg_maxconn: int = 20

    # AWS
    aws_url: str
    aws_region_name: str = "us-east-1"
    sqs_url: str = "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/ais_message_group"


    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"