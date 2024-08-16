from aiogram import Bot, Dispatcher #эта библиотека для бота и диспетчера
from aiogram.filters import Command #эта библиотека для комманд бота
from aiogram.types import Message #эта библиотека для сообщений бота
from aiogram.fsm.context import FSMContext #эта библиотека для хранения состояний бота
from aiogram.fsm.state import State, StatesGroup #эта библиотека для хранения состояний бота
from aiogram.fsm.storage.memory import MemoryStorage #эта библиотека для хранения состояний бота
import asyncio #эта библиотека для асинхронной работы с ботом
import logging #эта библиотека для логирования бота
import sqlite3 #эта библиотека для работы с базами данных (для хранения состояний бота)

API_TOKEN = ''

logging.basicConfig(level=logging.INFO)





class Form(StatesGroup): #класс для хранения состояний
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect("school_data.db") #подключение к базе данных
    cursor = conn.cursor() #создание курсора
    cursor.execute("""CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL 
            )""")
    conn.commit() #подтверждение изменений
    conn.close()



storage = MemoryStorage() #инициализация хранилища
bot = Bot(token=API_TOKEN) #инициализация бота
dp = Dispatcher(storage=storage) #инициализация диспетчера

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext): #функция для получения имени
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):#функция для получения возраста
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.answer("Ты какого класса?")
        await state.set_state(Form.grade)
    except ValueError:
        await message.answer("Ваши варианты: буржуазия, пролетариат, крестьяне, ремесленники, армия, духовенство, дворянство")

@dp.message(Form.grade)
async def get_grade(message: Message, state: FSMContext): #функция для получения класса
    await state.update_data(grade=message.text)
    data = await state.get_data()
    conn = sqlite3.connect("school_data.db") #подключение к базе данных
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (data["name"], data["age"], data["grade"]))
    conn.commit() #подтверждение изменений
    conn.close()


    await state.clear() #очистка состояний бота

async def main(): #функция для запуска бота
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())