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

@dp.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    bot_info = await bot.get_me()
    user_id = message.from_user.id
    my_link = f"https://t.me/{bot_info.username}?start={user_id}"
    
    if user_id == ADMIN_ID:
        await message.answer(
            f"👑 ВЫ АВТОРИЗОВАНЫ КАК АДМИНИСТРАТОР\n\n"
            f"🔗 Ваша анонимная ссылка:\n`{my_link}`"
        )
        return

    if command.args:
        target_id = int(command.args)
        if target_id != user_id:
            user_links[user_id] = target_id
            await message.answer("🎯 Вы перешли по анонимной ссылке! Задайте ваш вопрос...")
            return

    user_links[user_id] = ADMIN_ID
    await message.answer("👋 Напишите любой вопрос, и он будет отправлен анонимно.")

@dp.message()
async def handle_messages(message: Message):
    sender_id = message.from_user.id

    # --- ЛОГИКА ОТВЕТА (REPLY) ---
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
            await message.answer("⚠️ Не удалось найти адресата (возможно, бот был перезапущен).")
        return

    # --- ОТПРАВКА ВХОДЯЩЕГО СООБЩЕНИЯ ---
    target_id = user_links.get(sender_id, ADMIN_ID)

    if target_id == ADMIN_ID:
        admin_header = (
            f"📩 НОВОЕ ВХОДЯЩЕЕ СООБЩЕНИЕ\n"
            f"👤 От: {message.from_user.full_name}\n"
            f"🔗 Юзернейм: @{message.from_user.username or 'отсутствует'}\n"
            f"🆔 ID: `{sender_id}`\n"
            f"-----------------------------------\n"
        )
        
        try:
            if message.text:
                sent_msg = await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"{admin_header}💬 {message.text}"
                )
            else:
                sent_msg = await message.copy_to(
                    chat_id=ADMIN_ID,
                    caption=f"{admin_header}{message.caption or ''}"
                )

            # Сохраняем связку: ID сообщения у админа -> ID отправителя
            reply_tracker[sent_msg.message_id] = sender_id
            await message.answer("✅ Отправлено")
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки: {e}")
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
    
