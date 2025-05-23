import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
import asyncpg
from datetime import datetime
import asyncio
import aiohttp
from decimal import Decimal

# Настройка бота
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Функция подключения к БД
async def get_db():
    return await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='rgz',
        host='localhost',
        port=5432
    )

# Состояния FSM
class RegState(StatesGroup):
    waiting_for_username = State()

class AddOperationState(StatesGroup):
    waiting_for_type = State()
    waiting_for_sum = State()
    waiting_for_date = State()

class CurrencyChoiceState(StatesGroup):
    waiting_for_currency = State()

class OperationsDateState(StatesGroup):
    waiting_for_date_from = State()
    waiting_for_date_to = State()

# Регистрация
@dp.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext):
    db = await get_db()
    user = await db.fetchrow("SELECT * FROM users WHERE chat_id = $1", message.chat.id)
    if user:
        await message.answer("🫵 Вы уже зарегистрированы.")
        await db.close()
        return
    await message.answer("💅 Введите ваше имя (логин):")
    await state.set_state(RegState.waiting_for_username)
    await db.close()

@dp.message(RegState.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    db = await get_db()
    await db.execute("INSERT INTO users (name, chat_id) VALUES ($1, $2)", message.text, message.chat.id)
    await message.answer(f"🎉 Регистрация прошла успешно, {message.text}!")
    await db.close()
    await state.clear()

# Добавление операции
@dp.message(Command("add_operation"))
async def cmd_add_operation(message: Message, state: FSMContext):
    db = await get_db()
    user = await db.fetchrow("SELECT * FROM users WHERE chat_id = $1", message.chat.id)
    if not user:
        await message.answer("🙅‍♀️ Сначала зарегистрируйтесь командой /reg.")
        await db.close()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 ДОХОД 💰", callback_data="income")],
        [InlineKeyboardButton(text="💸 РАСХОД 💸", callback_data="expense")]
    ])
    await message.answer("🤔 Выберите тип операции:", reply_markup=keyboard)
    await state.set_state(AddOperationState.waiting_for_type)
    await db.close()

@dp.callback_query(AddOperationState.waiting_for_type)
async def process_type(callback: CallbackQuery, state: FSMContext):
    type_map = {"income": "ДОХОД", "expense": "РАСХОД"}
    await state.update_data(type_operation=type_map[callback.data])
    await callback.message.answer("💲 Введите сумму операции (в рублях):")
    await callback.answer()
    await state.set_state(AddOperationState.waiting_for_sum)

@dp.message(AddOperationState.waiting_for_sum)
async def process_sum(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Некорректное значение. Введите сумму в рублях, например: 1500.50")
        return
    await state.update_data(sum=amount)
    await message.answer("📆 Введите дату операции в формате ДД-ММ-ГГГГ:")
    await state.set_state(AddOperationState.waiting_for_date)

@dp.message(AddOperationState.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    try:
        date_obj = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате ДД-ММ-ГГГГ.")
        return

    data = await state.get_data()
    db = await get_db()
    await db.execute(
        "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES ($1, $2, $3, $4)",
        date_obj, data["sum"], message.chat.id, data["type_operation"]
    )
    await message.answer("✅ Операция успешно добавлена!")
    await db.close()
    await state.clear()

# Изменяем /operations, чтобы запускать FSM с запроса даты "с"
@dp.message(Command("operations"))
async def cmd_operations(message: Message, state: FSMContext):
    db = await get_db()
    user = await db.fetchrow("SELECT * FROM users WHERE chat_id = $1", message.chat.id)
    await db.close()

    if not user:
        await message.answer("🙅‍♀️ Сначала зарегистрируйтесь командой /reg.")
        return

    await message.answer("1️⃣ Введите начальную дату периода в формате ДД-ММ-ГГГГ:")
    await state.set_state(OperationsDateState.waiting_for_date_from)

# Обработка даты "с"
@dp.message(OperationsDateState.waiting_for_date_from)
async def process_date_from(message: Message, state: FSMContext):
    try:
        date_from = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате ДД-ММ-ГГГ.")
        return

    await state.update_data(date_from=date_from)
    await message.answer("2️⃣ Введите конечную дату периода в формате ДД-ММ-ГГГГ:")
    await state.set_state(OperationsDateState.waiting_for_date_to)

# Обработка даты "по"
@dp.message(OperationsDateState.waiting_for_date_to)
async def process_date_to(message: Message, state: FSMContext):
    try:
        date_to = datetime.strptime(message.text, "%d-%m-%Y").date()
    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате ДД-ММ-ГГГГ.")
        return

    data = await state.get_data()
    date_from = data.get("date_from")

    if date_to < date_from:
        await message.answer("⁉️ Конечная дата не может быть меньше начальной. Попробуйте снова.")
        return

    await state.update_data(date_to=date_to)

    # Предлагаем выбрать валюту
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="RUB", callback_data="RUB")],
        [InlineKeyboardButton(text="EUR", callback_data="EUR")],
        [InlineKeyboardButton(text="USD", callback_data="USD")]
    ])
    await message.answer("🤔 Выберите валюту для отображения операций:", reply_markup=keyboard)
    await state.set_state(CurrencyChoiceState.waiting_for_currency)

# Обработка выбора валюты с учетом диапазона дат
@dp.callback_query(CurrencyChoiceState.waiting_for_currency)
async def process_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data
    await callback.answer()

    data = await state.get_data()
    date_from = data.get("date_from")
    date_to = data.get("date_to")

    # Получение курса из внешнего сервиса
    rate = Decimal('1.0')
    if currency in ["EUR", "USD"]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:5000/rate?currency={currency}") as resp:
                    if resp.status == 200:
                        data_resp = await resp.json()
                        rate = Decimal(str(data_resp.get("rate", "1.0")))
                    else:
                        await callback.message.answer("💀 Ошибка получения курса валют.")
                        await state.clear()
                        return
        except Exception:
            await callback.message.answer("😭 Внешний сервис недоступен.")
            await state.clear()
            return

    # Запрос операций в БД за период
    db = await get_db()
    operations = await db.fetch(
        "SELECT * FROM operations WHERE chat_id = $1 AND date >= $2 AND date <= $3 ORDER BY date",
        callback.from_user.id, date_from, date_to
    )
    await db.close()

    if not operations:
        await callback.message.answer(f"😵 У вас нет операций с {date_from} по {date_to}.")
        await state.clear()
        return

    # Формируем сообщение с операциями
    text = f"🙌 Ваши операции с {date_from} по {date_to} в валюте {currency}:\n"
    for op in operations:
        date_str = op["date"].strftime("%d-%m-%Y")
        sum_converted = round(op["sum"] / rate, 2)
        text += f"{date_str}: {op['type_operation']} - {sum_converted} {currency}\n"

    await callback.message.answer(text)


if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())