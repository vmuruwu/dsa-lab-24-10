import asyncio
import uvicorn
from threading import Thread
from lab_6_bot import dp, bot

def run_currency_manager():
    uvicorn.run("lab_6_currency_manager:app", port=5001)

def run_data_manager():
    uvicorn.run("lab_6_data_manager:app", port=5002)

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Создаём поток для сервиса currency_manager
    t1 = Thread(target=run_currency_manager, daemon=True)
    # Создаём поток для сервиса data_manager
    t2 = Thread(target=run_data_manager, daemon=True)

    # Запускаем потоки — оба сервиса работают параллельно в фоне
    t1.start()
    t2.start()

    # Запускаем Telegram-бота в основном потоке с помощью asyncio
    asyncio.run(run_bot())
