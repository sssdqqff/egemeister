from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, text, URL
from config import settings

engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10,
)

with engine.connect() as connection:
    res = connection.execute(text("SELECT VERSION()"))
    print(res)