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
    await message.answer("Выберите тип операции:", reply_markup=keyboard)
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
    await message.answer("📆 Введите дату операции в формате ГГГГ-ММ-ДД:")
    await state.set_state(AddOperationState.waiting_for_date)

@dp.message(AddOperationState.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    try:
        date_obj = datetime.strptime(message.text, "%Y-%m-%d").date()
    except ValueError:
        await message.answer("❌ Неверный формат даты. Введите в формате ГГГГ-ММ-ДД.")
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

# 1-3. Команда /operations, проверка регистрации, выбор валюты
@dp.message(Command("operations"))
async def cmd_operations(message: Message, state: FSMContext):
    db = await get_db()
    user = await db.fetchrow("SELECT * FROM users WHERE chat_id = $1", message.chat.id)
    await db.close()

    if not user:
        await message.answer("🙅‍♀️ Сначала зарегистрируйтесь командой /reg.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="RUB", callback_data="RUB")],
        [InlineKeyboardButton(text="EUR", callback_data="EUR")],
        [InlineKeyboardButton(text="USD", callback_data="USD")]
    ])
    await message.answer("🤔 Выберите валюту для отображения операций:", reply_markup=keyboard)
    await state.set_state(CurrencyChoiceState.waiting_for_currency)


# 4–8. Обработка валюты, запрос к внешнему сервису, конвертация и вывод
@dp.callback_query(CurrencyChoiceState.waiting_for_currency)
async def process_currency(callback: CallbackQuery, state: FSMContext):
    currency = callback.data
    await callback.answer()

    # шаг 5. Получение курса из внешнего сервиса
    rate = 1.0
    if currency in ["EUR", "USD"]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:5000/rate?currency={currency}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        rate = data.get("rate", 1.0)
                    else:
                        await callback.message.answer("Ошибка получения курса валют.")
                        return
        except Exception:
            await callback.message.answer("Внешний сервис недоступен.")
            return

    # шаг 6. Получение операций
    db = await get_db()
    operations = await db.fetch("SELECT * FROM operations WHERE chat_id = $1", callback.from_user.id)
    await db.close()

    # шаг 7. Конвертация
    if not operations:
        await callback.message.answer("😵‍💫 У вас нет операций.")
        return

    rate = Decimal(str(rate))  # Приводим курс к Decimal

    text = f"🙌 Ваши операции в валюте {currency}:\n"
    for op in operations:
        date = op["date"].strftime("%d-%m-%Y")
        sum_converted = round(op["sum"] / rate, 2)
        text += f"{date}: {op['type_operation']} - {sum_converted} {currency}\n"

    # шаг 8. Вывод
    await callback.message.answer(text)
    await state.clear()


if __name__ == "__main__":
    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())
