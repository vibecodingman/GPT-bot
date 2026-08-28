import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import google.generativeai as genai

# 1. Вставьте сюда ваши бесплатные ключи
TELEGRAM_TOKEN = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"  # Получать бесплатно у @BotFather
GEMINI_API_KEY = "ВАШ_БЕСПЛАТНЫЙ_КЛЮЧ"  # Получать бесплатно в Google AI Studio

# Настройка нейросети
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Словарь для хранения истории диалога каждого пользователя
chats = {}

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    # Создаем или сбрасываем чат для пользователя
    chats[user_id] = model.start_chat(history=[])
    await message.answer("Привет! Я твой бесплатный ИИ-ассистент. Я запоминаю наш диалог, спрашивай о чем угодно!")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    
    # Если пользователь перезапустил бота или пишет впервые без /start
    if user_id not in chats:
        chats[user_id] = model.start_chat(history=[])
        
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем сообщение в текущую сессию чата (так сохраняется контекст)
        response = chats[user_id].send_message(message.text)
        await message.reply(response.text)
    except Exception as e:
        await message.reply("Ой, что-то пошло не так. Попробуйте еще раз.")
        print(f"Ошибка: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
