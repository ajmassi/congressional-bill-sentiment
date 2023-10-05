from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kafka
    kafka_bootstrap_servers: str
    kafka_bill_raw_topic: str
    kafka_bill_processed_topic: str

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
