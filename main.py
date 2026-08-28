import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from g4f.client import AsyncClient

# Токен вашего Telegram-бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Ошибка: Переменная окружения TELEGRAM_TOKEN не задана!")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализируем бесплатный клиент ИИ
ai_client = AsyncClient()

# Словарь для хранения истории сообщений каждого пользователя
user_histories = {}

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    user_histories[user_id] = []  # Очищаем память диалога
    await message.answer(
        "Привет! Я твой бесплатный ИИ-ассистент на базе ChatGPT.\n\n"
        "🧠 **Я помню длинный контекст нашей беседы!**\n"
        "🧹 Если захочешь стереть мне память и начать с чистого листа, напиши команду /clear"
    )

# Команда для ручной очистки памяти
@dp.message(Command("clear"))
async def clear_cmd(message: types.Message):
    user_id = message.from_user.id
    user_histories[user_id] = []
    await message.answer("🧹 Память успешно очищена! О чем пообщаемся теперь?")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Если пользователь пишет первый раз
    if user_id not in user_histories:
        user_histories[user_id] = []
        
    # Включаем анимацию "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Записываем то, что написал пользователь
    user_histories[user_id].append({"role": "user", "content": message.text})
    
    # УВЕЛИЧЕННЫЙ ЛИМИТ: Храним последние 40 сообщений (~20 вопросов и ~20 ответов)
    if len(user_histories[user_id]) > 40:
        user_histories[user_id] = user_histories[user_id][-40:]

    try:
        # Отправляем длинный запрос к ИИ
        response = await ai_client.chat.completions.create(
            model="gpt-4o",
            messages=user_histories[user_id]
        )
        
        bot_reply = response.choices.message.content
        
        # Запоминаем ответ бота
        user_histories[user_id].append({"role": "assistant", "content": bot_reply})
        
        # Отправляем ответ пользователю
        await message.reply(bot_reply)
        
    except Exception as e:
        await message.reply("Извините, нейросеть сейчас сильно загружена. Попробуйте отправить сообщение еще раз или очистите память командой /clear.")
        print(f"Ошибка g4f: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
