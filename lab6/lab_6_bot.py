import aiohttp
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
import asyncio
import os

# Configuration
API_TOKEN = os.getenv("API_TOKEN")
CURRENCY_MANAGER_URL = "http://localhost:5001"
DATA_MANAGER_URL = "http://localhost:5002"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# States
class CurrencyStates(StatesGroup):
    ADD_CURRENCY_NAME = State()
    ADD_CURRENCY_RATE = State()
    DELETE_CURRENCY = State()
    UPDATE_CURRENCY_NAME = State()
    UPDATE_CURRENCY_RATE = State()
    CONVERT_CURRENCY_NAME = State()
    CONVERT_AMOUNT = State()


async def make_async_request(url, method="GET", json_data=None, params=None):
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params) as response:
                return await response.json(), response.status
        elif method == "POST":
            async with session.post(url, json=json_data) as response:
                return await response.json(), response.status


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start."""
    commands = [
        "/manage_currency - Управление валютами",
        "/get_currencies - Список всех валют",
        "/convert - Конвертировать валюту в RUB"
    ]
    await message.answer("\n".join(commands))


@dp.message(Command("manage_currency"))
async def manage_currency(message: Message, state: FSMContext):
    """Меню управления валютами."""
    keyboard = [
        ["Добавить валюту", "Удалить валюту"],
        ["Изменить курс", "Отмена"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)
    await message.answer(
        "Выберите действие:",
        reply_markup=reply_markup
    )


@dp.message(F.text.casefold() == "добавить валюту")
async def add_currency_name(message: Message, state: FSMContext):
    """Запрос названия валюты для добавления."""
    await state.set_state(CurrencyStates.ADD_CURRENCY_NAME)
    await message.answer(
        "Введите название валюты:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(CurrencyStates.ADD_CURRENCY_NAME)
async def add_currency_rate(message: Message, state: FSMContext):
    """Запрос курса валюты."""
    await state.update_data(currency_name=message.text)

    # Проверка существования валюты
    response, status = await make_async_request(f"{DATA_MANAGER_URL}/currencies")
    if status == 200:
        currencies = response.get('currencies', [])
        for curr in currencies:
            if curr['currency'].lower() == message.text.lower():
                await message.answer("Данная валюта уже существует")
                await state.clear()
                return

    await state.set_state(CurrencyStates.ADD_CURRENCY_RATE)
    await message.answer("Введите курс к рублю:")


@dp.message(CurrencyStates.ADD_CURRENCY_RATE)
async def save_currency(message: Message, state: FSMContext):
    """Сохранение новой валюты."""
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Курс должен быть числом. Начните заново.")
        await state.clear()
        return

    data = await state.get_data()
    currency_name = data['currency_name']

    # Отправка в микросервис
    response, status = await make_async_request(
        f"{CURRENCY_MANAGER_URL}/load",
        method="POST",
        json_data={'currency_name': currency_name, 'rate': rate}
    )

    if status == 200:
        await message.answer(f"Валюта: {currency_name} успешно добавлена")
    else:
        await message.answer(f"Ошибка: {response.get('error', 'Неизвестная ошибка')}")

    await state.clear()


@dp.message(F.text.casefold() == "удалить валюту")
async def delete_currency(message: Message, state: FSMContext):
    """Запрос названия валюты для удаления."""
    await state.set_state(CurrencyStates.DELETE_CURRENCY)
    await message.answer(
        "Введите название валюты для удаления:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(CurrencyStates.DELETE_CURRENCY)
async def perform_delete(message: Message, state: FSMContext):
    """Удаление валюты."""
    currency_name = message.text

    # Отправка в микросервис
    response, status = await make_async_request(
        f"{CURRENCY_MANAGER_URL}/delete",
        method="POST",
        json_data={'currency_name': currency_name}
    )

    if status == 200:
        await message.answer(f"Валюта: {currency_name} успешно удалена")
    else:
        await message.answer(f"Ошибка: {response.get('error', 'Неизвестная ошибка')}")

    await state.clear()


@dp.message(F.text.casefold() == "изменить курс")
async def update_currency_name(message: Message, state: FSMContext):
    """Запрос названия валюты для изменения курса."""
    await state.set_state(CurrencyStates.UPDATE_CURRENCY_NAME)
    await message.answer(
        "Введите название валюты:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(CurrencyStates.UPDATE_CURRENCY_NAME)
async def update_currency_rate(message: Message, state: FSMContext):
    """Запрос нового курса валюты."""
    await state.update_data(currency_name=message.text)
    await state.set_state(CurrencyStates.UPDATE_CURRENCY_RATE)
    await message.answer("Введите новый курс к рублю:")


@dp.message(CurrencyStates.UPDATE_CURRENCY_RATE)
async def perform_update(message: Message, state: FSMContext):
    """Обновление курса валюты."""
    try:
        rate = float(message.text)
    except ValueError:
        await message.answer("Курс должен быть числом. Начните заново.")
        await state.clear()
        return

    data = await state.get_data()
    currency_name = data['currency_name']

    # Отправка в микросервис
    response, status = await make_async_request(
        f"{CURRENCY_MANAGER_URL}/update_currency",
        method="POST",
        json_data={'currency_name': currency_name, 'rate': rate}
    )

    if status == 200:
        await message.answer(f"Курс валюты {currency_name} успешно обновлен")
    else:
        await message.answer(f"Ошибка: {response.get('error', 'Неизвестная ошибка')}")

    await state.clear()


@dp.message(Command("get_currencies"))
async def get_currencies(message: Message):
    """Получение списка всех валют."""
    response, status = await make_async_request(f"{DATA_MANAGER_URL}/currencies")

    if status == 200:
        currencies = response.get('currencies', [])
        if currencies:
            message_text = "\n".join(
                f"{curr['currency']}: {curr['rate']} RUB"
                for curr in currencies
            )
        else:
            message_text = "Нет доступных валют"
    else:
        message_text = "Ошибка при получении списка валют"

    await message.answer(message_text)


@dp.message(Command("convert"))
async def convert_currency(message: Message, state: FSMContext):
    """Начало процесса конвертации."""
    await state.set_state(CurrencyStates.CONVERT_CURRENCY_NAME)
    await message.answer(
        "Введите название валюты:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(CurrencyStates.CONVERT_CURRENCY_NAME)
async def get_currency_amount(message: Message, state: FSMContext):
    """Запрос суммы для конвертации."""
    await state.update_data(currency_name=message.text)
    await state.set_state(CurrencyStates.CONVERT_AMOUNT)
    await message.answer("Введите сумму:")


@dp.message(CurrencyStates.CONVERT_AMOUNT)
async def perform_conversion(message: Message, state: FSMContext):
    """Выполнение конвертации и вывод результата."""
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Сумма должна быть числом. Начните заново.")
        await state.clear()
        return

    data = await state.get_data()
    currency_name = data['currency_name']

    # Отправка в микросервис
    response, status = await make_async_request(
        f"{DATA_MANAGER_URL}/convert",
        params={'currency': currency_name, 'amount': amount}
    )

    if status == 200:
        await message.answer(
            f"{response['original_amount']} {response['currency']} = "
            f"{response['converted_amount']} RUB (курс: {response['rate']})"
        )
    else:
        await message.answer(f"Ошибка: {response.get('error', 'Неизвестная ошибка')}")

    await state.clear()


@dp.message(F.text.casefold() == "отмена")
async def cancel(message: Message, state: FSMContext):
    """Отмена текущей операции."""
    await state.clear()
    await message.answer(
        "Операция отменена",
        reply_markup=ReplyKeyboardRemove()
    )


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())