from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # app
    app_name: str = "My Awesome App"
    debug_mode: bool = True

    # database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_psycopg(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

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