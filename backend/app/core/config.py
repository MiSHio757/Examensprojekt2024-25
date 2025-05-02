# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Läs från .env-filen i backend-mappen (där scriptet troligen körs ifrån)
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore') 

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: str = "5432" 
    POSTGRES_DB: str

    # Bygg ihop databas-URL för SQLAlchemy (asynkron version)
    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

# Använd lru_cache för att bara skapa Settings-objektet en gång
@lru_cache()
def get_settings() -> Settings:
    return Settings(_env_file='.env') 

# Gör settings tillgängligt för import
settings = get_settings()