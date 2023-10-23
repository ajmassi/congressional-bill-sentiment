from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kafka
    kafka_bootstrap_servers: str
    kafka_bill_processed_topic: str

    neo4j_url: str
    neo4j_user: str
    neo4j_user_password: str
    
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
