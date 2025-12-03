from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Kafka
    kafka_address: str = "localhost:9092"
    kafka_topic: str = "ais_message"
    kafka_retry_delay: int = 2

    # Websocket API
    ws_api_key: str = "90ebcd12a02888b382cf2c013bfd3336b2b82108"
    ws_api_url: str = "wss://stream.aisstream.io/v0/stream"
    ws_retry_seconds: int = 2

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"