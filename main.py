import logging
import asyncio
import requests
from aiogram.utils.callback_data import CallbackData
from bs4 import BeautifulSoup as b

from aiogram import Bot, Dispatcher, executor, utils, types
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from db import process_search_model, init_db, find_id_search, find_all_stuff, Dress
from config import URL, TOKEN
from parser1 import AllStuffParsing
import ui.buttons as b
import ui.slash_commands as slash


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.answer(f'Hey, {message.from_user.first_name}! I am your assistant in finding the right dresses and '
                         f'jumpsuits on the MANGO website in the USA. To read more about me, you can use /help command')


@dp.message_handler(commands='help')
async def send_help(message: types.Message):
    message_text = f'You can control me by sending these commands:\n' \
                   f'/list -  you get a list of all stuff\n' \
                   f'/search - you get a list of stuff with your filter\n' \
                   f'/type - you get a list of the type of clothing you have selected\n' \
                   f'/contact - you can contact developers with given links\n'
    await message.answer(text=message_text)


@dp.message_handler(commands='contact')
async def send_link(message: types.Message):
    buttons = [
        types.InlineKeyboardButton(text='Eva', url="https://t.me/evabronskayaa"),
        types.InlineKeyboardButton(text='Nadya', url="https://t.me/nodlya")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    await message.answer('Any questions? Have you find a bug? Notify developers 👇🏻', reply_markup=keyboard)


@dp.message_handler(commands='search')
async def send_search(message: types.Message):
    search_models = find_id_search(message.chat.id)
    for search_model in search_models:
        await message.answer(text=search_model.title)


@dp.message_handler(commands='list')
async def send_list(message: types.Message):
    search_models = find_id_search(message.chat.id)
    cards = find_all_stuff()
    for card in cards:
        card_title = card.title
        for search_model in search_models:
            search_title = search_model.title
            if card_title.find(search_title) >= 0:
                message_text = 'Строка поиска {} \r\nНайдено {}'.format(search_title, utils.markdown.hlink(card_title,
                                                                                                            card.url))
                await message.answer(text=message_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands='type')
async def send_type(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['All', 'Dresses', 'Jumpsuits']
    keyboard.add(*buttons)
    await message.answer('Well, let\'s choose cool looks! Tell me the type of clothes :)', reply_markup=keyboard)


# @dp.message_handler(Text(equals="All"))
# async def get_all(message: types.Message):
#     await message.reply("")
#
#
# @dp.message_handler(lambda message: message.text == "Dresses")
# async def get_dresses(message: types.Message):
#     await message.reply("")

@dp.message_handler()
async def echo(message: types.Message):
    await process_search_model(message)


async def scheduled(wait_for, parser):
    while True:
        await asyncio.sleep(wait_for)
        print('Parse')
        await parser.parse()


if __name__ == '__main__':
    init_db()
    parser = AllStuffParsing(url=URL, bot=bot)
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(10, parser))
    executor.start_polling(dp, skip_updates=True)
