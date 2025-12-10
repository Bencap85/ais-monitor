from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Kafka
    kafka_address: str = "kafka:9092"
    kafka_topic: str = "ais_message"
    kafka_retry_delay: int = 2

    # Websocket API
    ws_api_key: str
    ws_api_url: str = "wss://stream.aisstream.io/v0/stream"
    ws_retry_seconds: int = 2

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"