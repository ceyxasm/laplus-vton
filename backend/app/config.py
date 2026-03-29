from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS - set to "*" in production or comma-separated origins
    cors_origins: str = "*"

    # File Upload
    max_upload_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"

    # Mock Mode
    mock_mode: bool = False
    mock_delay: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
