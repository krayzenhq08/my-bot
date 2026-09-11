import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

BOT_TOKEN = "8807187343:AAEsVZ9ZDVXSCimengil2d8fC_JwEOBnC_4"
ADMIN_ID = 8846865308

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_links = {}     
reply_tracker = {}  

# 1. КОМАНДА /START
@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    bot_info = await bot.get_me()
    user_id = message.from_user.id
    my_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    # ПРОВЕРКА НА АДМИНА
    if user_id == ADMIN_ID:
        await message.answer(
            f"👑 **ВЫ АВТОРИЗОВАНЫ КАК АДМИНИСТРАТОР**\n\n"
            f"🔗 **Ваша личная анонимная ссылка:**\n`{my_link}`\n\n"
            f"Все входящие сообщения от других пользователей будут приходить с их данными (Имя, @username, ID)."
        )
        return

    # ЕСЛИ ОБЫЧНЫЙ ПОЛЬЗОВАТЕЛЬ ПЕРЕШЕЛ ПО ССЫЛКЕ
    if command.args:
        target_id = int(command.args)
        if target_id == user_id:
            await message.answer("Нельзя писать самому себе.")
            return
            
        user_links[user_id] = target_id
        await message.answer("🎯 Вы перешли по анонимной ссылке!\nЗадайте ваш вопрос...")
    else:
        # Если зашел без ссылки — по умолчанию пишет АДМИНУ
        user_links[user_id] = ADMIN_ID
        await message.answer(
            f"👋 Это бот анонимных вопросов!\n\n"
            f"Напишите любой вопрос или отправьте медиафайлы — они уйдут анонимно."
        )

# 2. ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
@dp.message()
async def handle_messages(message: Message):
    sender_id = message.from_user.id

    # --- ЕСЛИ АДМИН ОТВЕЧАЕТ НА СООБЩЕНИЕ (REPLY) ---
    if message.reply_to_message:
        reply_msg_id = message.reply_to_message.message_id
        original_sender = reply_tracker.get(reply_msg_id)
        
        if original_sender:
            try:
                # Отправляем ответ пользователю БЕЗ ваших данных
                await message.copy_to(chat_id=original_sender)
                await message.answer("✅ Ответ отправлен")
            except Exception:
                await message.answer("❌ Ошибка доставки (пользователь заблокировал бота)")
        else:
            await message.answer("⚠️ Не удалось найти адресата для ответа")
        return

    # --- ВСЕ ВХОДЯЩИЕ СООБЩЕНИЯ ОТ ПОЛЬЗОВАТЕЛЕЙ ---
    target_id = user_links.get(sender_id, ADMIN_ID)

    # Формируем шапку для ВАС (Админа)
    if target_id == ADMIN_ID:
        admin_header = (
            f"📩 **НОВОЕ ВХОДЯЩЕЕ СООБЩЕНИЕ**\n"
            f"👤 **От:** {message.from_user.full_name}\n"
            f"🔗 **Юзернейм:** @{message.from_user.username or 'отсутствует'}\n"
            f"🆔 **ID:** `{sender_id}`\n"
            f"-----------------------------------\n"
        )
        
        try:
            # Если это обычный текст
            if message.text:
                sent_msg = await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"{admin_header}💬 {message.text}"
                )
            # Если это фото, голосовое, видео или другой файл
            else:
                sent_msg = await message.copy_to(
                    chat_id=ADMIN_ID,
                    caption=f"{admin_header}{message.caption or ''}"
                )

            reply_tracker[sent_msg.message_id] = sender_id
            await message.answer("✅ Отправлено")
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки: {e}")

    # Формируем шапку для ОБЫЧНЫХ пользователей (если пишут не вам)
    else:
        try:
            sent_msg = await message.copy_to(
                chat_id=target_id,
                caption="📩 **Вам пришло новое анонимное сообщение!**"
            )
            reply_tracker[sent_msg.message_id] = sender_id
            await message.answer("✅ Отправлено")
        except Exception:
            await message.answer("❌ Не удалось отправить")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
