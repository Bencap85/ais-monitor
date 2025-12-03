from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    db_name: str = "ais_data"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "host.docker.internal"
    db_port: int = 5432
    db_max_history_per_mmsi: int = 100 # The max number of history positions to keep for every ship
    db_history_prune_query_interval: int = 5 # Schedule the history prune query to run every x minutes

    # Kafka
    kafka_address: str = "localhost:9092"
    kafka_topic: str = "ais_message"
    kafka_retry_delay: int = 2

    # Connection pool
    pg_minconn: int = 1
    pg_maxconn: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"