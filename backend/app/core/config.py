from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DASTAK_", env_file=".env", extra="ignore")

    env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    db_path: str = str(BACKEND_ROOT / "dastak_local.db")
    upload_dir: str = str(BACKEND_ROOT / "uploads")
    max_file_size_mb: int = 10
    retention_hours: int = 24
    model_dir: str = str(PROJECT_ROOT / "models")
    log_level: str = "INFO"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
