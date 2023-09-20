from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Congress API
    api_key: str
    url_param_congress: int
    url_param_format: str
    url_param_offset: int
    url_param_limit: int

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
