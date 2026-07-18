from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # app
    app_name: str = "My Awesome App"
    debug_mode: bool = True

    # database
    database_url: str
    db_echo: bool = True

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

    class Config:
        env_file = ".env"


settings = Settings()