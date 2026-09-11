import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

# Жестко прописанные данные
BOT_TOKEN = "8807187343:AAEsVZ9ZDVXSCimengil2d8fC_JwEOBnC_4"
ADMIN_ID = 8846865308

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_links = {}     
reply_tracker = {}  

# 1. ОБРАБОТКА КОМАНДЫ /START
@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    bot_info = await bot.get_me()
    user_id = message.from_user.id
    my_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    # ПРОВЕРКА: ЕСЛИ ПИШЕТЕ ВЫ (АДМИН)
    if user_id == ADMIN_ID:
        await message.answer(
            f"👑 **ВЫ АВТОРИЗОВАНЫ КАК АДМИНИСТРАТОР**\n\n"
            f"🔗 **Ваша личная анонимная ссылка:**\n`{my_link}`\n\n"
            f"Все вопросы, приходящие по этой ссылке, будут содержать данные отправителя (Имя, Username, ID)."
        )
        return

    # ЕСЛИ ПИШЕТ ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ
    if command.args:
        target_id = int(command.args)
        if target_id == user_id:
            await message.answer("Нельзя писать самому себе.")
            return
            
        user_links[user_id] = target_id
        await message.answer("🎯 Вы перешли по анонимной ссылке!\nЗадайте ваш вопрос...")
    else:
        await message.answer(
            f"👋 Это бот анонимных вопросов!\n\n"
            f"🔗 **Ваша анонимная ссылка:**\n`{my_link}`\n\n"
            f"Разместите её в профиле, чтобы получать вопросы!"
        )

# 2. ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
@dp.message()
async def handle_messages(message: Message):
    sender_id = message.from_user.id

    # --- ОТВЕТ НА СООБЩЕНИЕ (REPLY) ---
    if message.reply_to_message:
        reply_msg_id = message.reply_to_message.message_id
        original_sender = reply_tracker.get(reply_msg_id)
        
        if original_sender:
            try:
                await message.copy_to(chat_id=original_sender)
                await message.answer("✅ Ответ отправлен")
            except Exception:
                await message.answer("❌ Ошибка доставки")
        else:
            await message.answer("⚠️ Адресат не найден")
        return

    # --- ОТПРАВКА ВОПРОСА ---
    target_id = user_links.get(sender_id)
    if not target_id:
        target_id = ADMIN_ID

    # Если сообщение предназначено ВАМ (Админу) — показываем данные
    if target_id == ADMIN_ID:
        caption_text = (
            f"📩 **НОВОЕ СООБЩЕНИЕ (Для Админа)**\n"
            f"👤 **От:** {message.from_user.full_name}\n"
            f"🔗 **Юзернейм:** @{message.from_user.username or 'отсутствует'}\n"
            f"🆔 **ID:** `{sender_id}`"
        )
    else:
        # Для остальных людей — полная анонимность
        caption_text = "📩 **Новое анонимное сообщение**\n*(Ответьте на сообщение, чтобы отправить ответ)*"

    try:
        if message.text and target_id != ADMIN_ID:
            sent_msg = await bot.send_message(chat_id=target_id, text=f"{caption_text}\n\n💬 {message.text}")
        else:
            sent_msg = await message.copy_to(
                chat_id=target_id, 
                caption=caption_text if message.caption is None else f"{caption_text}\n\n{message.caption}"
            )

        reply_tracker[sent_msg.message_id] = sender_id
        await message.answer("✅ Отправлено")
    except Exception:
        await message.answer("❌ Не удалось отправить")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
        
