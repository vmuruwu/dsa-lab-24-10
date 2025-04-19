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

# Создание бота с токеном, который выдал в BotFather при регистрации бота
bot = Bot(token=API_TOKEN)
# Инициализация диспетчера команд
dp = Dispatcher()


# Генерация текста со списком команд
def get_help_text():
    return (
        "📜 Доступные команды:\n"
        "💲 /start - Начало работы с ботом\n"
        "💰 /save_currency - Сохранить курс валюты\n"
        "💸 /convert - Конвертировать валюту в рубли\n"
    )


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для учёта курсов валют.\n"
        f"{get_help_text()}"
    )


# Словарь для хранения валют
currency_dict = {}


# Состояния для сохранения валюты
class CurrencyForm(StatesGroup):
    name = State()
    rate = State()


# Состояния для конвертации
class ConvertForm(StatesGroup):
    currency_name = State()
    amount = State()


# Команда /save_currency — начало
@dp.message(Command("save_currency"))
async def save_currency(message: types.Message, state: FSMContext):
    await message.answer("💵 Введите название валюты (например, USD):")
    await state.set_state(CurrencyForm.name)


# Шаг b — пользователь вводит название валюты
@dp.message(CurrencyForm.name)
async def process_currency_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.upper())
    await message.answer("💹 Введите курс этой валюты к рублю (например, 91.5):")
    await state.set_state(CurrencyForm.rate)


# Шаг d — пользователь вводит курс валюты
@dp.message(CurrencyForm.rate)
async def process_currency_rate(message: types.Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
        data = await state.get_data()
        currency_name = data["name"]
        currency_dict[currency_name] = rate
        await message.answer(f"✅Сохранено: 1 {currency_name} = {rate} RUB")
    except ValueError:
        await message.answer("❌Пожалуйста, введите корректное число.")
        return
    await state.clear()


# Команда /convert — начало
@dp.message(Command("convert"))
async def convert_currency(message: types.Message, state: FSMContext):
    await message.answer("💵 Введите название валюты для конвертации (например, USD):")
    await state.set_state(ConvertForm.currency_name)


# Шаг b — пользователь вводит название валюты
@dp.message(ConvertForm.currency_name)
async def process_convert_currency_name(message: types.Message, state: FSMContext):
    currency_name = message.text.upper()
    if currency_name not in currency_dict:
        await message.answer(f"🥲 Валюта {currency_name} не найдена. Введите другую валюту.")
        return

    await state.update_data(currency_name=currency_name)
    await message.answer(f"🧮 Введите сумму в {currency_name} для конвертации в рубли:")
    await state.set_state(ConvertForm.amount)


# Шаг d — пользователь вводит сумму
@dp.message(ConvertForm.amount)
async def process_convert_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        data = await state.get_data()
        currency_name = data["currency_name"]
        rate = currency_dict[currency_name]
        result = amount * rate
        await message.answer(f"✅ {amount} {currency_name} = {result:.2f} RUB")
    except ValueError:
        await message.answer("❌Пожалуйста, введите корректное число.")
        return
    await state.clear()


# Запуск
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())