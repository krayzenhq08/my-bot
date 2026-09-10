import http.server, socketserver, threading, os
threading.Thread(target=lambda: socketserver.TCPServer(("", int(os.getenv("PORT", 10000))), http.server.SimpleHTTPRequestHandler).serve_forever(), daemon=True).start()
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Считываем токен и ID из настроек хостинга (для безопасности)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# ВСТАВЬТЕ СЮДА ВАШИ ID СТИКЕРОВ ИЗ ЭТАПА 1
STICKER_WELCOME = "CAACAgEAAxkBAAER4YJqoyUAARC6OeaMt8tRFy1qAUHKFm4AAhUCAAKh3uBHc1iFIXcgGWk9BA"  # Приветственный (для пользователей)
STICKER_SUCCESS = "CAACAgIAAxkBAAER4YRqoyVHfd3w5s_0WfFX3lSITZ90UAACDAIAAmkSAAImRL7VT3TbJD0E"  # Успешная отправка (принято/голубь/галочка)
STICKER_ADMIN = "CAACAgIAAxkBAAER4YZqoyV8Hqy6B_8p_kQYZjTMH5P7rwACvGEAArpkuUrtD-vhjvGwET0E"    # Для вас (босс/шпион/контроль)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        if STICKER_ADMIN and not STICKER_ADMIN.startswith("СЮДА"):
            await message.answer_sticker(STICKER_ADMIN)
        await message.answer("✨ **Режим Администратора активен**\n\nСюда будут поступать все входящие сообщения.")
    else:
        if STICKER_WELCOME and not STICKER_WELCOME.startswith("СЮДА"):
            await message.answer_sticker(STICKER_WELCOME)
        await message.answer(
            "🔮 **Добро пожаловать!**\n\n"
            "Здесь вы можете задать любой вопрос или оставить сообщение абсолютно анонимно.\n\n"
            "👇 *Просто напишите ваш текст или отправьте файл ниже:*"
        )

@dp.message()
async def forward_to_admin(message: types.Message):
    # Стелс-режим для вас (ответы никому не уходят)
    if message.from_user.id == ADMIN_ID:
        await message.answer("🔒 *[Стелс-режим]* Сообщение сохранено приватным и никому не отправлено.")
        return

    user = message.from_user
    username = f"@{user.username}" if user.username else "отсутствует"
    
    # Красивая карточка входящего сообщения
    user_card = (
        "📥 **НОВОЕ ВХОДЯЩЕЕ СООБЩЕНИЕ**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Отправитель:** {user.full_name}\n"
        f"🏷 **Юзернейм:** {username}\n"
        f"🆔 **ID:** `{user.id}`\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "👇 **Содержимое:**"
    )

    # Пересылка вам в личку
    await bot.send_message(chat_id=ADMIN_ID, text=user_card, parse_mode="Markdown")
    await message.copy_to(chat_id=ADMIN_ID)

    # Ответ пользователю
    if STICKER_SUCCESS and not STICKER_SUCCESS.startswith("СЮДА"):
        await message.answer_sticker(STICKER_SUCCESS)
    await message.answer("🕊 *Ваше сообщение успешно отправлено!*")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
