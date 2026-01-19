from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    history_prune_enabled: bool = False
    max_history_per_mmsi: str = str(100) # The max number of history positions to keep for every ship
    history_prune_query_interval: str = str(5) # Schedule the history prune query to run every x minutes

    # Database
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "host.docker.internal"
    db_port: str = str(5432)

    # Connection pool
    pg_minconn: int = 1
    pg_maxconn: int = 20

    # AWS
    aws_url: str | None = None
    aws_region_name: str = "us-east-1"
    repository_queue_url: str

    base_path: str = "/repository/api/v1"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"

settings = Settings()