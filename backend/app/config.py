from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    mongo_url: str = "mongodb://localhost:27017"
    mongo_db: str = "billrecon"
    redis_url: str = "redis://localhost:6380/0"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "documents"
    minio_secure: bool = False
    max_upload_mb: int = 10
    # Comma-separated web origins allowed to call the API. 3000 is often taken locally, so 3100 is allowed too.
    cors_origins: str = "http://localhost:3000,http://localhost:3100"


settings = Settings()
