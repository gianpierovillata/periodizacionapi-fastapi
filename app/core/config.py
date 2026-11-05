from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Periodizacion API"
    api_v1_prefix: str = "/api/v1"
    # Orígenes del frontend que pueden llamar a la API desde el navegador.
    cors_origins: list[str] = ["http://localhost:5173"]

    mysql_host: str = "db"
    mysql_port: int = 3306
    mysql_database: str
    mysql_user: str
    mysql_password: str

    @property
    def database_url(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
