from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"
BMI_ASSETS_DIR = ASSETS_DIR / "bmi"
BODY_ASSETS_DIR = ASSETS_DIR / "body"
PRODUCT_ASSETS_DIR = ASSETS_DIR / "product"
CERTIFICATES_ASSETS_DIR = ASSETS_DIR / "certificates"
EXERCISES_ASSETS_DIR = ASSETS_DIR / "exercises"
GENERATED_ASSETS_DIR = ASSETS_DIR / "generated"


def ensure_asset_directories() -> None:
    directories = [
        ASSETS_DIR,
        BMI_ASSETS_DIR,
        BODY_ASSETS_DIR,
        PRODUCT_ASSETS_DIR,
        CERTIFICATES_ASSETS_DIR,
        EXERCISES_ASSETS_DIR,
        GENERATED_ASSETS_DIR,
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )


ensure_asset_directories()


class Settings(BaseSettings):
    bot_token: str

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    database_url: str = (
        "sqlite+aiosqlite:///./slimwell.db"
    )

    admin_ids: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def admins(self) -> set[int]:
        result: set[int] = set()

        for value in self.admin_ids.split(","):
            value = value.strip()

            if value.isdigit():
                result.add(
                    int(value)
                )

        return result

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()

        if url.startswith("postgres://"):
            return url.replace(
                "postgres://",
                "postgresql+asyncpg://",
                1,
            )

        if url.startswith("postgresql://"):
            return url.replace(
                "postgresql://",
                "postgresql+asyncpg://",
                1,
            )

        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
