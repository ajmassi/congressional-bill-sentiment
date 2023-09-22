import pathlib

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Congress API
    api_key: str
    url_base: str
    url_congress: int
    url_param_format: str
    url_param_bill_limit: int

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

        # absolute path for current directory
        secrets_dir = f"{pathlib.Path(__file__).parent.resolve()}/secrets"


settings = Settings()
