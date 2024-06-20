import os
from flask import Flask
from threading import Thread

import asyncio
import logging
import random
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage




app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Initialize bot and dispatcher
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
# Инициализация логгера для aiogram
logging.basicConfig(level=logging.INFO)
# Словарь для хранения информации о последнем использовании команды прогноза на день
user_last_daily_forecast = {}

# Словарь с путями к gif-файлам и их описаниями
gif_data = {
    'data/cards/00.gif': "Ідея, думка, духовність, те, що прагне піднестися над матеріальним (якщо предмет, який ворожать, пов'язані з духовним). У гаданні на матеріальний об'єкт, пов'язаний із повсякденним життям, карта вважається поганою, вона означає необачність, дурість, ексцентричність, манію і навіть психічну хворобу.",
    'data/cards/01.gif': "Вміння, мудрість, пристосованість, здатність, розум і хитрість, спритність і так далі завжди спираються на гідність. Іноді окультна мудрість.",
    'data/cards/02.gif': "Мудрість, знання, зміна, зміна, збільшення та зменшення. Коливання",
    'data/cards/03.gif': "Краса, щастя, задоволення, успіх, розкіш. У дуже поганій гідності карта означає розсіяння, безпутний спосіб життя.",
    'data/cards/04.gif': "Війна, завоювання та підкорення, перемога, сварка, честолюбство, втілення, розвиток, досягнення.",
    'data/cards/05.gif': "Божественна мудрість, милосердя, вияв, пояснення, вчення. У деяких аспектах збігається за значенням з картами Маг, Путівник і Закохані. Окультна мудрість.",
    'data/cards/06.gif': "Натхнення. Мотив, дія та влада, що виникають з натхнення та пориву.",
    'data/cards/07.gif': "Тріумф, перемога, подолання перешкод, здоров'я. Успіх, щоправда часом швидкоплинний і нестабільний.",
    'data/cards/08.gif': "Сміливість, мужність, могутність, сила духу та стійкість. Сила непереборна, подібна до суду, що завершує справу. Іноді символізує тупу завзятість та перевищення влади.",
    'data/cards/09.gif': "Мудрість згори, яку шукають і обрядять. Розсудливість і далекоглядність, передбачливість та роздуми. Божественне натхнення.",
    'data/cards/10.gif': "Добрий успіх і щастя, але в певних межах. У поганій гідності: сп'яніння успіхом чи невдача, а також провал, якщо інші карти, що лежать поруч, це підтверджують.",
    'data/cards/11.gif': "Вічна правосуддя та рівновага, баланс. Сила і міць, але стримані, так само як і в процесі суду. Також у комбінаціях з іншими картами юридичні процедури, слухання справи в суді, суд, випробування судом тощо. У поганій гідності: жорстокість та упередження.",
    'data/cards/12.gif': "Покарання. Втрата. Страждання взагалі. Жертва не завжди добровільна.",
    'data/cards/13.gif': "Часи. Століття. Перетворення. Зміна. Ненавмисне зміна, на противагу Місяцю. Іноді смерть і руйнація, останнє, щоправда, дуже рідко.",
    'data/cards/14.gif': "Поєднання, комбінація сил. Реалізація. Об'єднання. Матеріальна дія, результат якої може бути як хорошим, так і поганим.",
    'data/cards/15.gif': "Матеріальність. Матеріальна сила. Спокуса матеріальна або іноді нав'язлива ідея, особливо якщо карта пов'язана з закоханими.",
    'data/cards/16.gif': "Амбіція, боротьба, сварка, війна, хоробрість. Порівняйте з Імператором. У поганій гідності у деяких поєднаннях: руйнація, аварія, падіння, небезпека.",
    'data/cards/17.gif': "Надія, віра, несподівана допомога. У поганій гідності: мрійливість, ошукана надія.",
    'data/cards/18.gif': "Незадоволеність, добровільна зміна (на противагу карті Смерть). У поганій гідності помилка, брехня, фальш, обман.",
    'data/cards/19.gif': "Слава, вигода та придбання, багатство, щастя, радість. У поганій гідності: марнославство, зарозумілість, чванлива показуха.",
    'data/cards/20.gif': "Остаточне рішення, судження, вирок, результат, визначення будь-якої справи чи питання без надії на апеляцію чи перегляд. У поганому гідності: відкладання справи.",
    'data/cards/21.gif': "Матерія, сутність, синтез, завершення, винагорода. Світ, царство. Зазвичай означає суть питання і тому цілком залежить від навколишніх карток.",
    # Добавьте свои gif-изображения и описания сюда
}

# Функция для отправки случайного gif и описания
async def send_daily_forecast(user_id):
    # Получаем список ключей (путей к gif-файлам)
    gif_files = list(gif_data.keys())

    if not gif_files:
        await bot.send_message(user_id, "Вибачте, немає доступних gif-зображень зараз.")
        return

    # Выбираем случайный gif-файл
    gif_path = random.choice(gif_files)
    description = gif_data[gif_path]

    # Отправляем gif и описание пользователю
    gif_file = types.FSInputFile(gif_path)
    await bot.send_document(user_id, gif_file, caption=description)

    # Обновляем время последнего использования команды
    user_last_daily_forecast[user_id] = datetime.datetime.now()

    # Создаем клавиатуру с кнопками меню
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="Прогноз на день 🙏")],
        [KeyboardButton(text="⭐ Мої послуги")],
        [KeyboardButton(text="Мій рахунок 💰")],
        [KeyboardButton(text="❓❓❓ Задати питання")]
    ])

    # Отправляем сообщение с меню
    await bot.send_message(user_id, "Виберіть пункт меню👇:", reply_markup=keyboard)

# Обработчик команды /start
@router.message(Command("start"))
async def process_start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="Прогноз на день 🙏")],
        [KeyboardButton(text="⭐ Мої послуги")],
        [KeyboardButton(text="Мій рахунок 💰")],
        [KeyboardButton(text="❓❓❓ Задати питання")]
    ])
    await message.answer("Виберіть пункт меню👇:", reply_markup=keyboard)

# Словарь для хранения состояния пользователей
user_states = {}

# Обработчик текстовых сообщений
@router.message(lambda message: message.text in ["Прогноз на день 🙏", "⭐ Мої послуги", "Мій рахунок 💰", "❓❓❓ Задати питання"])
async def process_text_message(message: types.Message):
    user_id = message.from_user.id
    action = message.text

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="Прогноз на день 🙏")],
        [KeyboardButton(text="⭐ Мої послуги")],
        [KeyboardButton(text="Мій рахунок 💰")],
        [KeyboardButton(text="❓❓❓ Задати питання")]
    ])

    if action == "Прогноз на день 🙏":
        # Проверяем, прошло ли уже 24 часа с последнего использования
        last_used = user_last_daily_forecast.get(user_id)
        if last_used and (datetime.datetime.now() - last_used).total_seconds() < 86400:
            await message.answer("Ви вже одержали прогноз на сьогодні!\nНапишіть своє запитання або запишіться на прийом👇", reply_markup=keyboard)
        else:
            await send_daily_forecast(user_id)
    elif action == "⭐ Мої послуги":
        await message.answer("Індивідуальні розклади Таро по всім життєвим ситуаціям:\n🧑‍💼Робота\n💵Фінанси\n💌Кохання\n⚕️Здоров’я", reply_markup=keyboard)
    elif action == "Мій рахунок 💰":
        await message.answer("ПриватБанк: \n4149609029416874 ", reply_markup=keyboard)
    elif action == "❓❓❓ Задати питання":
        user_states[user_id] = "awaiting_question"
        await message.answer("Будь ласка, введіть ваше запитання❓", reply_markup=keyboard)

# Обработчик сообщений пользователей
@router.message(lambda message: user_states.get(message.from_user.id) == "awaiting_question")
async def handle_question(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name  # Имя пользователя
    user_question = message.text

    # Отправка вопроса администратору
    await bot.send_message(ADMIN_ID, f"Питання від користувача {user_name} (ID: {user_id}):\n{user_question}")

    # Сброс состояния пользователя
    user_states[user_id] = None

    # Создаем клавиатуру с кнопками меню
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, keyboard=[
        [KeyboardButton(text="Прогноз на день 🙏")],
        [KeyboardButton(text="⭐ Мої послуги")],
        [KeyboardButton(text="Мій рахунок 💰")],
        [KeyboardButton(text="❓❓❓ Задати питання")]
    ])

    # Создаем inline-клавиатуру для ответа
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Відповісти користувачеві", callback_data=f"answer:{user_id}")]
    ])

    # Отправляем сообщение с подтверждением и inline-кнопкой "Ответить"
    await message.answer("Ваше запитання надіслано адміністратору. Чекайте на відповідь⏲️", reply_markup=keyboard)
    await bot.send_message(ADMIN_ID, "Натисніть нижче, щоб відповісти на запитання користувача👇", reply_markup=inline_keyboard)

# Обработчик callback-запросов для ответа на вопрос пользователя
@router.callback_query(lambda c: c.data and c.data.startswith('answer:'))
async def process_callback_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split(':')[1]
    user_id = int(user_id)

    # Ответ администратору с приглашением отправить сообщение
    await bot.send_message(callback_query.from_user.id, f"Введіть відповідь для користувача з ID: {user_id}")

    # Сохранение состояния админа для дальнейшего ответа
    user_states[callback_query.from_user.id] = f"answering:{user_id}"

# Обработчик текстовых сообщений от администратора для отправки ответа пользователю
@router.message(lambda message: user_states.get(message.from_user.id, "").startswith("answering:"))
async def handle_admin_answer(message: types.Message):
    admin_id = message.from_user.id
    state = user_states.get(admin_id, "")
    if state:
        user_id = int(state.split(':')[1])
        answer_text = message.text

        # Отправляем ответ пользователю
        await bot.send_message(user_id, f"Відповідь від 😀 адміністратора: {answer_text}")

        # Подтверждаем администратору, что ответ был отправлен
        await message.answer("Відповідь надіслано користувачу🙏")

        # Сбрасываем состояние администратора
        user_states[admin_id] = None



# Регистрация роутеров и запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
     # Запуск веб-сервера для UptimeRobot
    keep_alive()
    asyncio.run(main())
