from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite+aiosqlite:///./slimwell.db"
    admin_ids: str = ""
    start_id: int = 12345

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def admins(self) -> set[int]:
        result: set[int] = set()
        for item in self.admin_ids.split(","):
            item = item.strip()
            if item.isdigit():
                result.add(int(item))
        return result

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()

