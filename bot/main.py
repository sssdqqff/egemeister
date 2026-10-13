import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str
    bot_api_key: str
    api_base_url: str = "http://127.0.0.1:8000"


settings = Settings()
dp = Dispatcher()


@dp.message(CommandStart(), F.chat.type == "private")
async def handle_start(message: Message, http: httpx.AsyncClient) -> None:
    user = message.from_user
    try:
        response = await http.post(
            "/internal/bot/login-codes",
            json={"telegram_id": user.id, "first_name": user.first_name},
        )
    except httpx.HTTPError:
        await message.answer("Сервис временно недоступен. Попробуйте чуть позже.")
        return
    if response.status_code == 403:
        await message.answer("Доступ к аккаунту закрыт.")
        return
    if response.status_code != 200:
        logging.error("login-codes failed with status %s", response.status_code)
        await message.answer("Не получилось создать код. Попробуйте чуть позже.")
        return
    data = response.json()
    minutes = max(data["expires_in"] // 60, 1)
    await message.answer(
        f"🔑 Ваш код для входа:\n\n<code>{data['code']}</code>\n\n"
        f"Нажмите на код, чтобы скопировать. Он действителен {minutes} мин."
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    async with httpx.AsyncClient(
        base_url=settings.api_base_url,
        headers={"X-Bot-Key": settings.bot_api_key},
        timeout=10,
    ) as http:
        await dp.start_polling(bot, http=http)


if __name__ == "__main__":
    asyncio.run(main())