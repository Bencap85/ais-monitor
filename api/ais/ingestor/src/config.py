from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    ais_message_batch_size: str
    
    # Websocket API
    ws_api_key: str
    ws_api_url: str = "wss://stream.aisstream.io/v0/stream"
    ws_retry_seconds: int = 2

    # AWS
    aws_url: str | None = None
    aws_region_name: str = "us-east-1"
    sns_topic_arn: str = "arn:aws:sns:us-east-1:000000000000:ais_message"

    base_path: str = "/ingestor/api/v1"
 
    class Config:
        env_file = "../../.env"
        env_file_encoding = "utf-8"

settings = Settings()