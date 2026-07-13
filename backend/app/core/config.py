from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Muhasebe Entegrasyon WebApp"
    ENV: str = "development"

    # Üretimde .env üzerinden mutlaka değiştirilmeli.
    SECRET_KEY: str = "CHANGE_ME_dev_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8

    DATABASE_URL: str = "sqlite:///./dev.db"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # "mock" | "zirve"
    # "zirve" -> ZirAPI (Zeruxsoft) üzerinden çalışır. API key .env'de değil,
    # admin panelindeki Muhasebe Ayarları ekranından girilir ve DB'de şifreli
    # saklanır (bkz. CLAUDE.md -> Zirve Entegrasyon Notları).
    ACCOUNTING_PROVIDER: str = "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
