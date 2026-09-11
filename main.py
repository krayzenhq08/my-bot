import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

BOT_TOKEN = "8807187343:AAEsVZ9ZDVXSCimengil2d8fC_JwEOBnC_4"
ADMIN_ID = 8846865308

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# База данных в памяти: кто кому сейчас пишет и кто от кого получает ответы
user_links = {}     # ID отправителя -> ID получателя
reply_tracker = {}  # ID сообщения в чате -> ID исходного отправителя

@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    bot_info = await bot.get_me()
    user_id = message.from_user.id
    
    # Если перешли по чьей-то анонимной ссылке
    if command.args:
        target_id = int(command.args)
        if target_id == user_id:
            await message.answer("❌ Нельзя писать самому себе!")
            return
            
        user_links[user_id] = target_id
        await message.answer("🎯 Вы перешли по анонимной ссылке!\nОтправьте сообщение, фото или голосовое — оно уйдёт 100% анонимно.")
    else:
        # Генерация собственной ссылки для любого пользователя
        my_link = f"https://t.me/{bot_info.username}?start={user_id}"
        await message.answer(
            f"👋 Это бот анонимных вопросов!\n\n"
            f"🔗 **Ваша личная ссылка:**\n`{my_link}`\n\n"
            f"Разместите её у себя в профиле, чтобы получать анонимные сообщения!"
        )

@dp.message()
async def handle_messages(message: Message):
    sender_id = message.from_user.id

    # --- ЛОГИКА ОТВЕТА НА СООБЩЕНИЕ (REPLY) ---
    if message.reply_to_message:
        reply_msg_id = message.reply_to_message.message_id
        original_sender = reply_tracker.get(reply_msg_id)
        
        if original_sender:
            try:
                # Отправляем ответ анонимно (без раскрытия того, кто отвечает)
                await message.copy_to(chat_id=original_sender)
                await message.answer("✅ Ваш ответ анонимно отправлен!")
            except Exception:
                await message.answer("❌ Не удалось доставить ответ (пользователь заблокировал бота).")
        else:
            await message.answer("⚠️ Не удалось найти адресата для этого ответа.")
        return

    # --- ЛОГИКА ОТПРАВКИ НОВОГО ВОПРОСА ---
    # Определяем, кому предназначается сообщение
    target_id = user_links.get(sender_id)
    
    # Если человек не переходил по ссылке, но пишет в бота — по умолчанию отправляем ВАМ (Админу)
    if not target_id:
        target_id = ADMIN_ID

    # Формируем подпись
    if target_id == ADMIN_ID:
        # Для ВАС: показываем имя, юзернейм и ID отправителя
        caption_text = (
            f"📩 **ВХОДЯЩЕЕ СООБЩЕНИЕ (Для Админа)**\n"
            f"👤 От: {message.from_user.full_name}\n"
            f"🔗 Юзернейм: @{message.from_user.username or 'отсутствует'}\n"
            f"🆔 ID: `{sender_id}`"
        )
    else:
        # Для ОБЫЧНЫХ пользователей: ПОЛНАЯ анонимность (никаких ID и имён)
        caption_text = "📩 **Вам пришло новое анонимное сообщение!**\n\n*(Ответьте на это сообщение, чтобы отправить ответ)*"

    try:
        # Отправляем копию сообщения получателю
        if message.text and target_id != ADMIN_ID:
            sent_msg = await bot.send_message(chat_id=target_id, text=f"{caption_text}\n\n💬 {message.text}")
        else:
            sent_msg = await message.copy_to(chat_id=target_id, caption=caption_text if message.caption is None else f"{caption_text}\n\n{message.caption}")

        # Запоминаем ID сообщения, чтобы работала кнопка Reply (Ответ)
        reply_tracker[sent_msg.message_id] = sender_id
        await message.answer("🚀 Сообщение анонимно доставлено!")
    except Exception:
        await message.answer("❌ Не удалось отправить сообщение.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
