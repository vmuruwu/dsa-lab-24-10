import os
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.filters import Command
import re
import logging
from decimal import Decimal
from aiogram import F

# Настройка бота
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_COMMANDS = ['start', 'manage_currency', 'get_currencies', 'convert']
USER_COMMANDS = ['start', 'get_currencies', 'convert']

#Меню
user_commands = [
    BotCommand(command="start", description="Запуск"),
    BotCommand(command="get_currencies", description="Список валют"),
    BotCommand(command="convert", description="Конвертация"),
]

admin_commands = [
    BotCommand(command="start", description="Запуск"),
    BotCommand(command="manage_currency", description="Управление валютами"),
    BotCommand(command="get_currencies", description="Список валют"),
    BotCommand(command="convert", description="Конвертация"),
]

# Логирование
logging.basicConfig(level=logging.INFO)
# Инициализация бота
bot = Bot(token=API_TOKEN)

dp = Dispatcher()

# Подключение к базе данных
async def create_db_connection():
    return await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='tg_bot_vt',
        host='localhost',
        port=5432
    )

# Состояния для FSM
class CurrencyStates(StatesGroup):
    waiting_for_currency_name = State()
    waiting_for_currency_rate = State()
    waiting_for_currency_to_delete = State()
    waiting_for_currency_to_update = State()
    waiting_for_new_rate = State()
    waiting_for_convert_currency = State()
    waiting_for_convert_amount = State()

# Проверка является ли пользователь админом
async def is_admin(chat_id):
    conn = await create_db_connection()
    admin = await conn.fetchrow("SELECT * FROM admins WHERE chat_id = $1", chat_id)
    await conn.close()
    return admin is not None

async def set_bot_commands():
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())

    # Получаем список всех админов из базы данных
    conn = await create_db_connection()
    admins = await conn.fetch("SELECT chat_id FROM admins")
    await conn.close()

    # Устанавливаем команды для каждого админа
    for admin in admins:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin['chat_id']))

# Команда start
@dp.message(Command('start'))
async def cmd_start(message: Message):
    is_user_admin = await is_admin(str(message.from_user.id))

    if is_user_admin:
        response = (
            "👋 Привет, админ!\n\n"
            "📜 Доступные команды:\n"
            "💲 /start - Показать это меню\n"
            "💾 /manage_currency - Управление валютами (добавить/изменить/удалить)\n"
            "📊 /get_currencies - Показать список валют\n"
            "💸 /convert - Конвертировать валюту в рубли\n"
        )
    else:
        response = (
            "👋 Добро пожаловать!\n\n"
            "📜 Доступные команды:\n"
            "💲 /start - Показать это меню\n"
            "📊 /get_currencies - Показать список валют\n"
            "💸 /convert - Конвертировать валюту в рубли\n"
        )

    await message.answer(response)

# Команда manage_currency (только для админов)
@dp.message(Command('manage_currency'))
async def cmd_manage_currency(message: Message):
    if not await is_admin(str(message.from_user.id)):
        await message.answer("Нет доступа к команде")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить валюту"),
                KeyboardButton(text="Удалить валюту"),
                KeyboardButton(text="Изменить курс валюты")
            ]
        ],
        resize_keyboard=True
    )

    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message(F.text == "Добавить валюту")
async def add_currency_start(message: Message, state: FSMContext):
    await state.set_state(CurrencyStates.waiting_for_currency_name)
    await message.answer("Введите название валюты (до 5 символов)", reply_markup=ReplyKeyboardRemove())

# Получение названия валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency_name = message.text.strip().upper()[:5]

    if len(currency_name) < 1:
        await message.answer("Название валюты должно содержать от 1 до 5 символов")
        return

    conn = await create_db_connection()
    try:
        existing_currency = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1", currency_name
        )
        if existing_currency:
            await message.answer("Данная валюта уже существует")
            await state.clear()
            return

        await state.update_data(currency_name=currency_name)
        await state.set_state(CurrencyStates.waiting_for_currency_rate)
        await message.answer("Введите курс к рублю (число с максимум 2 знаками после запятой)")
    finally:
        await conn.close()

# Получение курса валюты для добавления
@dp.message(CurrencyStates.waiting_for_currency_rate)
async def process_currency_rate(message: Message, state: FSMContext):
    try:
        rate = round(float(message.text), 2)
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное положительное число для курса (например: 75.50)")
        return

    user_data = await state.get_data()
    currency_name = user_data['currency_name']

    conn = await create_db_connection()
    try:
        await conn.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)",
            currency_name, rate
        )
        await message.answer(f"Валюта: {currency_name} с курсом {rate} RUB успешно добавлена")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении валюты: {str(e)}")
    finally:
        await conn.close()
        await state.clear()

# Обработка кнопки "Удалить валюту"
@dp.message(F.text == "Удалить валюту")
async def delete_currency_start(message: Message, state: FSMContext):
    if not await is_admin(str(message.from_user.id)):
        await message.answer("Нет доступа к команде")
        return

    conn = await create_db_connection()
    try:
        currencies = await conn.fetch("SELECT currency_name FROM currencies ORDER BY currency_name")
        if not currencies:
            await message.answer("Нет доступных валют для удаления", reply_markup=ReplyKeyboardRemove())
            return

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=currency['currency_name'])] for currency in currencies],
            resize_keyboard=True
        )
        await state.set_state(CurrencyStates.waiting_for_currency_to_delete)
        await message.answer("Выберите валюту для удаления:", reply_markup=keyboard)
    finally:
        await conn.close()

# Получение названия валюты для удаления
@dp.message(CurrencyStates.waiting_for_currency_to_delete)
async def process_currency_to_delete(message: Message, state: FSMContext):
    currency_name = message.text.strip().upper()

    conn = await create_db_connection()
    try:
        existing_currency = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1", currency_name
        )
        if not existing_currency:
            await message.answer("Данная валюта не существует")
            await state.clear()
            return
        await conn.execute(
            "DELETE FROM currencies WHERE currency_name = $1",
            currency_name
        )
        await message.answer(f"Валюта {currency_name} успешно удалена", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"Ошибка при удалении валюты: {str(e)}", reply_markup=ReplyKeyboardRemove())
    finally:
        await conn.close()
        await state.clear()


# Обработка кнопки "Изменить курс валюты"
@dp.message(F.text == "Изменить курс валюты")
async def update_currency_start(message: Message, state: FSMContext):
    if not await is_admin(str(message.from_user.id)):
        await message.answer("Нет доступа к команде")
        return

    conn = await create_db_connection()
    try:
        currencies = await conn.fetch("SELECT currency_name FROM currencies ORDER BY currency_name")
        if not currencies:
            await message.answer("Нет доступных валют для изменения", reply_markup=ReplyKeyboardRemove())
            return

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=currency['currency_name'])] for currency in currencies],
            resize_keyboard=True
        )
        await state.set_state(CurrencyStates.waiting_for_currency_to_update)
        await message.answer("Выберите валюту для изменения курса:", reply_markup=keyboard)
    finally:
        await conn.close()

# Получение названия валюты для изменения
@dp.message(CurrencyStates.waiting_for_currency_to_update)
async def process_currency_to_update(message: Message, state: FSMContext):
    currency_name = message.text.strip().upper()

    conn = await create_db_connection()
    try:
        existing_currency = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1", currency_name
        )
        if not existing_currency:
            await message.answer("Данная валюта не существует")
            await state.clear()
            return

        await state.update_data(currency_name=currency_name)
        await state.set_state(CurrencyStates.waiting_for_new_rate)
        await message.answer("Введите новый курс к рублю (число с максимум 2 знаками после запятой)",
                           reply_markup=ReplyKeyboardRemove())
    finally:
        await conn.close()

# Получение нового курса валюты
@dp.message(CurrencyStates.waiting_for_new_rate)
async def process_new_rate(message: Message, state: FSMContext):
    try:
        new_rate = round(float(message.text), 2)
        if new_rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное положительное число для курса (например: 75.50)")
        return

    user_data = await state.get_data()
    currency_name = user_data['currency_name']

    conn = await create_db_connection()
    try:
        await conn.execute(
            "UPDATE currencies SET rate = $1 WHERE currency_name = $2",
            new_rate, currency_name
        )
        await message.answer(f"Курс валюты {currency_name} успешно изменён на {new_rate} RUB")
    except Exception as e:
        await message.answer(f"Ошибка при изменении курса: {str(e)}")
    finally:
        await conn.close()
        await state.clear()


# Команда get_currencies (для всех пользователей)
@dp.message(Command('get_currencies'))
async def cmd_get_currencies(message: Message):
    conn = await create_db_connection()
    try:
        currencies = await conn.fetch("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
        if not currencies:
            await message.answer("Нет доступных валют")
            return

        response = "Доступные валюты:\n"
        for currency in currencies:
            response += f"{currency['currency_name']}: {currency['rate']:.2f} RUB\n"

        await message.answer(response)
    finally:
        await conn.close()


# Обработка команды /convert (для всех пользователей)
@dp.message(Command('convert'))
async def cmd_convert(message: Message, state: FSMContext):
    conn = await create_db_connection()
    currencies = await conn.fetch("SELECT currency_name FROM currencies ORDER BY currency_name")
    await conn.close()

    if not currencies:
        await message.answer("Список валют пуст. Добавьте хотя бы одну валюту.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=currency['currency_name'])] for currency in currencies],
        resize_keyboard=True
    )

    await state.set_state(CurrencyStates.waiting_for_convert_currency)
    await message.answer("Введите название валюты для конвертации:", reply_markup=keyboard)

# Получение названия валюты для конвертации
@dp.message(CurrencyStates.waiting_for_convert_currency)
async def process_convert_currency(message: Message, state: FSMContext):
    currency_name = message.text.strip().upper()

    conn = await create_db_connection()
    try:
        currency = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1", currency_name
        )
        if not currency:
            await message.answer("Данная валюта не найдена")
            await state.clear()
            return

        await state.update_data(currency_name=currency_name, rate=currency['rate'])
        await state.set_state(CurrencyStates.waiting_for_convert_amount)
        await message.answer("Введите сумму для конвертации:")
    finally:
        await conn.close()


# Получение суммы для конвертации и вывод результата
@dp.message(CurrencyStates.waiting_for_convert_amount)
async def process_convert_amount(message: Message, state: FSMContext):
    text = message.text.strip().replace(",", ".")

    if not re.match(r'^-?\d+(\.\d+)?$', text):
        await message.answer("Пожалуйста, введите число")
        return

    amount = Decimal(text)
    if amount <= 0:
        await message.answer("Сумма должна быть положительной")
        return

    user_data = await state.get_data()
    currency_name = user_data['currency_name']
    rate = user_data['rate']

    result = amount * rate

    await message.answer(f"{amount} {currency_name} = {result:.2f} RUB")
    await state.clear()

# Запуск бота
async def main():
    await set_bot_commands()
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())