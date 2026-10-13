from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # app
    app_name: str = "Egemeister"
    debug_mode: bool = False

    # database
    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str
    database_echo: bool = False

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    # jwt auth
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # cors
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # static
    static_dir: str = "static"
    images_dir: str = "static/images"

    # telegram auth
    bot_api_key: str
    login_code_length: int = 6
    login_code_ttl_seconds: int = 300
    session_ttl_days: int = 30
    session_cookie_name: str = "egemeister_session"
    cookie_secure: bool = True
    cookie_samesite: str = "lax"

    login_max_failures: int = 5
    login_failure_window_seconds: int = 300
    api_origins: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]


settings = Settings()