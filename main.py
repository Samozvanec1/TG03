from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import aiohttp
import logging
import sqlite3

API_TOKEN = '7409932170:AAHcOW33Hdb87tHFXshCLVZZoMxalf4_JaQ'
WEATHER_API_KEY = '36a4f6fa8b6860533a636d4c755cbc8e'

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()

def init_db():
    conn = sqlite3.connect("databs.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        city TEXT NOT NULL,
        chat_id INTEGER NOT NULL
    )""")
    conn.commit()
    conn.close()

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("В каком городе ты живёшь?")
        await state.set_state(Form.city)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный возраст числом.")

@dp.message(Form.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    conn = sqlite3.connect("databs.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, age, city, chat_id) VALUES (?, ?, ?, ?)", (data["name"], data["age"], data["city"], message.chat.id))
    conn.commit()
    conn.close()

    session_timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={data['city']}&appid={WEATHER_API_KEY}&units=metric") as resp:
            if resp.status == 200:
                weather_data = await resp.json()
                main = weather_data["main"]
                weather = weather_data["weather"][0]

                temperature = main["temp"]
                description = weather["description"]
                humidity = main["humidity"]

                weather_report = (f"Город: {weather_data['name']}\nТемпература {temperature}°C.\nВлажность {humidity} %.\nОписание: {description}")
                await message.answer(weather_report)
            else:
                await message.answer("Не удалось получить погоду.")
    await state.clear()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())