import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncio


# Логирование
logging.basicConfig(level=logging.INFO)

# Получение токена из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")

#Создание бота с токеном, который выдал в BotFather при регистрации бота
bot = Bot(token=API_TOKEN)

#Инициализация диспетчера команд
dp = Dispatcher()

@dp.message(Command("start"))
async def start (message: types.Message):
    await message.answer('Привет')



# Словарь для хранения валют
currency_dict = {}

# Состояния
class CurrencyForm(StatesGroup):
    name = State()
    rate = State()

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Напиши /save_currency, чтобы сохранить курс валюты.")

# Команда /save_currency — начало
@dp.message(Command("save_currency"))
async def save_currency(message: types.Message, state: FSMContext):
    await message.answer("Введите название валюты (например, USD):")
    await state.set_state(CurrencyForm.name)

# Шаг b — пользователь вводит название валюты
@dp.message(CurrencyForm.name)
async def process_currency_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.upper())
    await message.answer("Введите курс этой валюты к рублю (например, 91.5):")
    await state.set_state(CurrencyForm.rate)

# Шаг d — пользователь вводит курс валюты
@dp.message(CurrencyForm.rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
        data = await state.get_data()
        currency_name = data["name"]
        currency_dict[currency_name] = rate
        await message.answer(f"Сохранено: 1 {currency_name} = {rate} RUB")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        return
    await state.clear()

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())