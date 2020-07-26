
import os
import logging

import sentry_sdk
from aiogram import Bot, Dispatcher, executor, types

from datetime import datetime, timedelta
import sys
sys.path[0] = '/app'
import pypi_tools.data as d
from pypi_tools import __version__
from pypi_tools.models import init_db, User, Chat


logging.basicConfig(level=logging.INFO)

sentry_sdk.init(os.environ["SENTRY_PATH"])

bot = Bot(token=os.environ["BOT_API_KEY"])
dp = Dispatcher(bot)

current_version = f"Current pypi_tools_bot version: {__version__}\n"

help_text = "Commands: \n\n" \
            "You can use command <i><b>'/search'</b></i> to find any package on PyPi and /search:detailed "\
            "if you want more detailed info.\n Example: /search aiohttp\n\n" \
            "Use <i><b> '/stats'</b></i> command to get download statistics for Python Package. \n" \
            "Example: /stats gino-admin\n\n"


def validate_input(text, command, custom_error=None, additional_error=None):
    split_message = text.split()
    if len(split_message) == 1:
        if not custom_error:
            output = f"To use command please provide package name after '/{command}' command. \n " \
                     f"Example: '/{command} aiohttp'"
        else:
            output = custom_error
        if additional_error:
            output += additional_error
    else:
        output = text.split()[1].replace('_', '-')
    return output


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    print(message.__dict__)
    print(message.chat.__dict__)
    if 'db' not in dp.__dict__:
        dp.__dict__['db'] = await init_db()
    user_id = message.chat.username
    user = await User.get(user_id)
    if not user:
        user = await User.create(**{'id': user_id,
                                    'first_name': message.chat.first_name,
                                    'last_name': message.chat.last_name})
    chat_id = message.chat.id
    chat = await Chat.get(chat_id)
    if not chat:
        chat = await Chat.create(**{'id': chat_id,
                                    'type': message.chat.type})
    else:
        chat_new = chat.to_dict()
        await chat.update(**chat_new).apply()
    text = f"Hello, {message.chat.first_name} {message.chat.last_name}! \n" \
           f"Welcome to <b>PyPi Tools Bot.</b>\n\n" \
           "This Bot created special to obtain information from Official Python PyPi Server\n" \
           + help_text + current_version

    await message.answer(text, parse_mode="html")


@dp.message_handler(commands=['help'])
async def send_welcome(message):
    await message.answer(help_text)


@dp.message_handler(commands=['stats'])
async def send_package_stats(message):
    output = validate_input(text=message.text, command="stats")
    if len(output.split()) == 1:
        package_name = output
        output = f"Stats for package <b>{package_name}</b> (numbers of downloads): \n\n"
        threads = []
        results = []
        from concurrent.futures import ThreadPoolExecutor, as_completed
        executor = ThreadPoolExecutor(5)
        tasks = [d.bq_get_downloads_stats_for_package(
            package_name, (datetime.now().date() - timedelta(days=i+1)).isoformat())
            for i in range(5)]

        for job in tasks:
            threads.append(executor.submit(job.result))

        for future in as_completed(threads):
            results.append(list(future.result()))
        print(results)
        for i in range(5):
            date_ = (datetime.now().date() - timedelta(days=i+1))
            downloads = results[i][0].downloads
            output += f"<b>{date_}</b>: {downloads}\n"
    await message.answer(output, parse_mode="html")


@dp.message_handler(commands=['random'])
async def command(message):
    # if :packages
    text = message.text
    error = "Or use with sub-command to get detailed information:" \
            "/random 5"
    output = validate_input(text=message.text, command="stats", custom_error=error)
    if len(output.split()) == 1:
        package_name = output
    else:
        message = output
    await message.answer(message)


@dp.message_handler(commands=['search', 'search:detailed'])
async def search_command(message):
    text = message.text
    known_commands = {'detailed': lambda _package_name: d.request_package_info_from_pypi(_package_name, detailed=True)}

    if ':' in text:
        # if /search:detailed
        sub_command, package_name = text.split(':')[1].split()
        if sub_command in known_commands:
            _answer = await known_commands[sub_command](package_name)
        else:
            _answer = f"Unknown sub-command {sub_command}. Possible sub-commands: {known_commands}"
    else:
        split_message = text.split()
        if len(split_message) > 1:
            package_name = split_message[1]
            _answer = await d.request_package_info_from_pypi(package_name)
        else:
            _answer = "To use command please provide package name after '/search' command. \n " \
                      "Example: '/search aiohttp'" \
                      "Or use with sub-command to get detailed information:" \
                      "/search:detailed aiohttp"
    await message.answer(_answer, parse_mode="html")


@dp.message_handler(commands=['track'])
async def track_command(message):
    print(message)
    await message.answer(message)


@dp.message_handler()
async def echo_all(message):
    await message.answer(message, message.text)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        sentry_sdk.capture_exception(e)

