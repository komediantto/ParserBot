import datetime
import logging
import json
import os
import string
from collections import Counter

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Command, IDFilter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegraph import Telegraph

from create_bot import bot
from misc import rate_limit
from parsing import (get_holidays, get_horoscope, get_info_from_bga,
                     get_info_from_bn, get_info_from_brgaz,
                     get_info_from_bryanskobl, get_info_from_gub,
                     get_info_from_newbryansk, get_info_from_ria,
                     get_urgent_information, get_urgent_information_polling,
                     get_weather)

load_dotenv()

scheduler = AsyncIOScheduler(timezone='UTC')
telegraph = Telegraph(os.getenv('TELEGRAPH_TOKEN'))


async def send_urgent_info(id):
    """
    It gets a list of urgent information from the database, formats it into a
    message, and sends it to the user

    :param id: the user's id
    """
    ads = get_urgent_information()
    message = 'Сводка новостей за прошедшие сутки\n\n'
    for ad in ads.items():
        message += f'{ad[0]}\n{ad[1]}\n\n'
    await bot.send_message(id, message, parse_mode='HTML')


async def send_horoscope(id):
    today = datetime.datetime.now().strftime('%d.%m.%Y года')
    await bot.send_message(id, f'ГОРОСКОП НА {today}')
    horoscopes = get_horoscope()
    for horoscope in horoscopes.items():
        await bot.send_photo(id, types.InputFile(horoscope[1][1]),
                             caption=f'{horoscope[0]}\n\n{horoscope[1][0]}',
                             parse_mode='HTML')


async def send_forecast(id, day):
    if day == 'today':
        date = datetime.datetime.now().strftime('%d.%m.%Y года')
        forecasts = get_weather()['today']
    elif day == 'tomorrow':
        date = (datetime.datetime.now() + datetime.timedelta(1)
                ).strftime('%d.%m.%Y года')
        forecasts = get_weather()['tomorrow']
    message = f'ПРОГНОЗ ПОГОДЫ на {date}\n\n'
    for forecast in forecasts.items():
        message += forecast[0] + '\n'
    photo = types.InputFile(Counter(forecasts.values()).most_common(1)[0][0])
    await bot.send_photo(id, photo, caption=message)


async def send_holidays(id):
    today = datetime.datetime.now().strftime('%d.%m.%Y года')
    holidays = get_holidays()
    message = f'ПРАЗДНИКИ {today}\n\n'
    for holiday in holidays:
        message += '🎉 ' + holiday + '\n'
    await bot.send_message(id, message)


async def send_info_polling(id):
    thing = get_urgent_information_polling()
    if thing is not None:
        try:
            photo = types.InputFile('images/Сайт МЧС основной.jpg')
            await bot.send_photo(id, photo,
                                 caption=thing, parse_mode='HTML')
        except Exception as e:
            logging.error('Слишком длинное сообщение')
            logging.error(e)
            photo = types.InputFile('images/Сайт МЧС основной.jpg')
            await bot.send_photo(id, photo)
            await bot.send_message(id, thing, parse_mode='HTML')


async def send_info_newbryansk_polling(id):
    for thing in get_info_from_newbryansk():
        try:
            if thing is not None:
                await bot.send_photo(id, thing[0],
                                     caption=thing[1], parse_mode='HTML')
        except Exception:
            logging.info('Слишком длинное сообщение')
            await bot.send_photo(id, thing[0])
            await bot.send_message(id, thing[1], parse_mode='HTML')


async def send_info_ria_polling(id):
    thing = get_info_from_ria()
    if thing is not None:
        await bot.send_photo(id, thing[0],
                             caption=thing[1], parse_mode='HTML')


async def send_info_bga_polling(id):
    thing = get_info_from_bga()
    try:
        if thing is not None:
            await bot.send_photo(id, thing[0],
                                 caption=thing[1], parse_mode='HTML')
    except Exception:
        logging.info('Слишком длинное сообщение')
        await bot.send_photo(id, thing[0])
        await bot.send_message(id, thing[1], parse_mode='HTML')


async def send_info_bo_polling(id):
    thing = get_info_from_bryanskobl()
    try:
        if thing is not None:
            if thing[0] is not None:
                await bot.send_photo(id, thing[0],
                                     caption=thing[1], parse_mode='HTML')
            else:
                await bot.send_message(id, thing[1], parse_mode='HTML')
    except Exception:
        logging.info('Слишком длинное сообщение')
        await bot.send_photo(id, thing[0])
        await bot.send_message(id, thing[1], parse_mode='HTML')


async def send_info_gub_polling(id):
    for thing in get_info_from_gub():
        try:
            if thing is not None:
                if thing[0] is not None:
                    await bot.send_photo(id, thing[0],
                                         caption=thing[1], parse_mode='HTML')
                else:
                    await bot.send_message(id, thing[1], parse_mode='HTML')
        except Exception:
            logging.info('Слишком длинное сообщение')
            await bot.send_photo(id, thing[0])
            await bot.send_message(id, thing[1], parse_mode='HTML')


async def send_info_brgaz_polling(id):
    thing = get_info_from_brgaz()
    try:
        if thing is not None:
            await bot.send_photo(id, thing[0],
                                 caption=thing[1], parse_mode='HTML')
    except Exception:
        logging.info('Слишком длинное сообщение')
        await bot.send_photo(id, thing[0])
        await bot.send_message(id, thing[1], parse_mode='HTML')


async def send_info_bn_polling(id):
    thing = get_info_from_bn()
    try:
        if thing is not None:
            await bot.send_photo(id, thing[0],
                                 caption=thing[1], parse_mode='HTML')
    except Exception:
        logging.info('Слишком длинное сообщение')
        await bot.send_photo(id, thing[0])
        await bot.send_message(id, thing[1], parse_mode='HTML')


async def start(message: types.Message):
    """
    It starts a scheduler that runs a bunch of functions at certain times.

    :param message: types.Message - the message that the user sent to the bot
    :type message: types.Message
    """
    cnl_id = os.getenv('CHANNEL_ID')
    an_cnl_id = os.getenv('ANOTHER_CHANNEL_ID')
    scheduler.add_job(send_urgent_info, 'cron',
                      args=[cnl_id], hour=4, misfire_grace_time=None)
    scheduler.add_job(send_horoscope, 'cron', args=[cnl_id],
                      hour=4, minute=45, misfire_grace_time=None)
    scheduler.add_job(send_forecast, 'cron', args=[cnl_id, 'today'],
                      hour=4, minute=30, misfire_grace_time=None)
    scheduler.add_job(send_holidays, 'cron', args=[cnl_id],
                      hour=6, misfire_grace_time=None)
    scheduler.add_job(send_info_polling, 'interval',
                      args=[cnl_id], minutes=1, misfire_grace_time=None)
    scheduler.add_job(send_info_newbryansk_polling, 'interval',
                      args=[cnl_id], minutes=1, seconds=3,
                      misfire_grace_time=None)
    scheduler.add_job(send_info_ria_polling, 'interval',
                      args=[an_cnl_id], minutes=1,
                      seconds=6, misfire_grace_time=None)
    scheduler.add_job(send_info_bga_polling, 'interval',
                      args=[cnl_id], minutes=1,
                      seconds=9, misfire_grace_time=None)
    scheduler.add_job(send_info_bo_polling, 'interval',
                      args=[cnl_id], minutes=1, seconds=12,
                      misfire_grace_time=None)
    scheduler.add_job(send_forecast, 'cron', args=[cnl_id, 'tomorrow'],
                      hour=18, misfire_grace_time=None)
    scheduler.add_job(send_info_gub_polling, 'interval', args=[cnl_id,],
                      minutes=1, seconds=15, misfire_grace_time=None)
    scheduler.add_job(send_info_brgaz_polling, 'interval', args=[cnl_id,],
                      minutes=1, seconds=17, misfire_grace_time=None)
    scheduler.add_job(send_info_bn_polling, 'interval', args=[cnl_id,],
                      minutes=1, seconds=17, misfire_grace_time=None)


@rate_limit(limit=1.5)
async def censorship(message: types.Message):
    """
    If the message contains a word from the list of forbidden words, then the
    message is deleted and the user is notified that the message was deleted

    :param message: types.Message - this is the message object that is passed
    to the function
    :type message: types.Message
    """
    raw_message = message.text.replace('\n', ' ')
    data = json.load(open('forbidden_words.json', encoding='utf-8'))
    profanity_list = []
    for i in data:
        profanity_list.append(i['word'])
    if {i.lower()
        .translate(str.maketrans('', '', string.punctuation)
                   ) for i in raw_message.split(' ')}.intersection(
                       set(profanity_list)) != set():
        await message.reply('Маты запрещены')
        await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(start, Command('start'))
    dp.register_message_handler(
        censorship, IDFilter(chat_id=os.getenv('COMMENT_GROUP_ID')))
