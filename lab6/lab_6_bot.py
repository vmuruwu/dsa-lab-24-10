import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
import logging

# Настройка бота
API_TOKEN = os.getenv("API_TOKEN")

# Логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

state = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Управление валютами", callback_data="manage")
    kb.button(text="Курсы валют", callback_data="currencies")
    kb.button(text="Конвертация", callback_data="convert")
    await message.answer("Выберите команду:", reply_markup=kb.as_markup())


@dp.callback_query()
async def general_callback_handler(callback: CallbackQuery):
    data = callback.data

    if data == "manage":
        kb = InlineKeyboardBuilder()
        kb.button(text="Добавить валюту", callback_data="add")
        kb.button(text="Удалить валюту", callback_data="delete")
        kb.button(text="Изменить курс", callback_data="update")
        await callback.message.answer("Выберите действие:", reply_markup=kb.as_markup())

    elif data == "currencies":
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:5002/currencies") as resp:
                if resp.status != 200:
                    await callback.message.answer("Ошибка при получении списка валют.")
                    return
                data = await resp.json()

        text = "Список валют:\n"
        for c in data:
            text += f"{c['currency_name']}: {c['rate']}\n"
        await callback.message.answer(text)

    elif data == "convert":
        state[callback.from_user.id] = {"action": "convert"}
        await callback.message.answer("Введите название валюты:")

    elif data in ["add", "delete", "update"]:
        action = data
        state[callback.from_user.id] = {"action": action}
        await callback.message.answer("Введите название валюты:")

    else:
        await callback.answer("Неизвестная команда")


@dp.message()
async def handle_text(message: Message):
    user_id = message.from_user.id
    if user_id not in state:
        return
    user_state = state[user_id]
    action = user_state.get("action")

    if action in ("add", "delete", "update"):
        if "currency_name" not in user_state:
            user_state["currency_name"] = message.text.upper()
            if action == "add":
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:5002/currencies") as resp:
                        if resp.status != 200:
                            await message.answer("Ошибка при получении списка валют.")
                            del state[user_id]
                            return
                        data = await resp.json()
                        if any(c["currency_name"] == user_state["currency_name"] for c in data):
                            await message.answer("Данная валюта уже существует")
                            del state[user_id]
                            return
                await message.answer("Введите курс к рублю:")

            elif action == "delete":
                async with aiohttp.ClientSession() as session:
                    async with session.post("http://localhost:5001/delete", json={"currency_name": user_state["currency_name"]}) as resp:
                        if resp.status == 200:
                            await message.answer("Валюта удалена")
                        elif resp.status == 404:
                            await message.answer("Такой валюты нет")
                        else:
                            await message.answer("Произошла ошибка при удалении валюты")
                del state[user_id]

            elif action == "update":
                await message.answer("Введите новый курс:")

        else:
            try:
                rate = float(message.text)
            except ValueError:
                await message.answer("Введите корректное число для курса.")
                return
            payload = {
                "currency_name": user_state["currency_name"],
                "rate": rate
            }
            url = "http://localhost:5001/load" if action == "add" else "http://localhost:5001/update_currency"
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        await message.answer(f"Валюта {user_state['currency_name']} успешно обработана")
                    elif resp.status == 404:
                        await message.answer("Такой валюты нет")
                    else:
                        await message.answer("Произошла ошибка при обработке валюты")
            del state[user_id]

    elif action == "convert":
        if "currency_name" not in user_state:
            user_state["currency_name"] = message.text.upper()
            await message.answer("Введите сумму:")
        else:
            try:
                amount = float(message.text)
            except ValueError:
                await message.answer("Введите корректное число для суммы.")
                return
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:5002/convert?currency_name={user_state['currency_name']}&amount={amount}") as resp:
                    if resp.status != 200:
                        await message.answer("Ошибка при конвертации валюты.")
                        del state[user_id]
                        return
                    data = await resp.json()
                    await message.answer(f"Сумма в рублях: {data['converted_amount']}")
            del state[user_id]


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
