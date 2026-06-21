from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    app_name: str = "Claude Session Analyzer"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    db_path: str = "data/sessions.db"
    sessions_dir: str = str(Path.home() / ".claude" / "projects")

    cors_origins: list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def db_full_path(self) -> Path:
        return Path(self.db_path).resolve()

    @property
    def sessions_full_dir(self) -> Path:
        return Path(self.sessions_dir).resolve()

    class Config:
        env_file = ".env"


settings = Settings()
