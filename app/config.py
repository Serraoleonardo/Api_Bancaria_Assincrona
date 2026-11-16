from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./banco.db"
    secret_key: str = "troque-esta-chave-secreta-em-producao-123"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
