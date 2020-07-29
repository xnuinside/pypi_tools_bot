
import os
import logging
from functools import wraps
import sentry_sdk
from aiogram import Bot, Dispatcher, executor, types
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pypi_tools.logic import validate_input_logic
import pypi_tools.data as d
import pypi_tools.readme as r
from pypi_tools.models import init_db, User, Chat


logging.basicConfig(level=logging.INFO)

sentry_sdk.init(os.environ["SENTRY_PATH"])

bot = Bot(token=os.environ["BOT_API_KEY"], parse_mode="html")
dp = Dispatcher(bot)


def validate_input(command, custom_error=None, additional_error=None, known_sub_commands=None):
    def validate_input_inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            message = args[0]
            output, sub_command = validate_input_logic(
                message, command, custom_error, additional_error, known_sub_commands)
            message.output = output
            message.sub_command = sub_command
            result = func(message)
            return result
        return wrapper
    return validate_input_inner


@dp.message_handler(commands=['start'])
async def send_welcome(message):
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
        await Chat.create(**{'id': chat_id, 'type': message.chat.type})
    else:
        chat_new = chat.to_dict()
        await chat.update(**chat_new).apply()
    text = f"Hello, {message.chat.first_name} {message.chat.last_name}! \n" \
           f"Welcome to <b>PyPi Tools Bot.</b>\n\n" \
           "This Bot created special to obtain information from Official Python PyPi Server\n" \
           + r.help_text + r.current_version

    await message.answer(text)


@dp.message_handler(commands=['help'])
async def send_welcome(message):
    await message.answer(r.help_text)


@dp.message_handler(lambda message: message.text and (
        '/stats' in message.text.lower() or 'stats:' in message.text.lower()))
@validate_input(command='stats',
                known_sub_commands={'@any_number': lambda num: num})
async def send_package_stats(message):
    output = message.output
    sub_command = message.sub_command or 5
    if len(output.split()) == 1:
        days = sub_command
        package_name = output
        output = f"Stats for package <b>{package_name}</b> \nfor last {days} days (numbers of downloads): \n\n"
        threads = []
        results = []
        executor = ThreadPoolExecutor(4)
        tasks = [d.bq_get_downloads_stats_for_package(
            package_name, (datetime.now().date() - timedelta(days=i+1)).isoformat())
            for i in range(days)]
        for job in tasks:
            threads.append(executor.submit(job.result))
        for future in as_completed(threads):
            results.append(list(future.result()))
        temp_result = {}
        for i in range(days):
            date_ = int(results[i][0].date)
            downloads = results[i][0].downloads
            temp_result[date_] = downloads
        sorted_dict = dict(sorted(temp_result.items(), reverse=True))
        for key, item in sorted_dict.items():
            output += f"<b>{datetime.strptime(str(key), '%Y%m%d').date().isoformat()}</b>: {item}\n"
    await message.answer(output)


@dp.message_handler(commands=['random'])
async def command(message):
    output = await d.get_random_package()
    await message.answer(output)


@dp.message_handler(commands=['search', 'search:detailed'])
@validate_input(command='search',
                known_sub_commands={'detailed': lambda _package_name: d.request_package_info_from_pypi(
                    _package_name, detailed=True)},
                additional_error="Or use with sub-command to get detailed information:"
                                 "/search:detailed aiohttp")
async def search_command(message):
    output = message.output
    sub_command = message.sub_command
    if len(output.split()) == 1:
        package_name = output
        if sub_command:
            output = await sub_command(package_name)
        else:
            output = await d.request_package_info_from_pypi(package_name)
    await message.answer(output)


@dp.message_handler(commands=['releases', 'releases:full'])
@validate_input(command='releases',
                known_sub_commands={'full': 'full'},
                additional_error="Or use with sub-command to get full list of releases:"
                                 "/releases:full aiohttp")
async def releases_command(message):
    output = message.output
    sub_command = message.sub_command
    if len(output.split()) == 1:
        package_name = output
        releases = await d.get_release_list(package_name=package_name)
        if sub_command and sub_command == 'full':
            output = f"Full Releases list for Package {package_name}\n\n"
            for version, v_date in releases.items():
                output += f"<b>{version}</b>: {v_date}\n"
        else:
            output = f"Last 7 Releases for Package {package_name}\n\n"
            for num, items in enumerate(list(releases.items())):
                if num > 7:
                    break
                version, v_date = items
                output += f"<b>{version}</b>: {v_date}\n"
    await message.answer(output)


@dp.message_handler(commands=['track'])
@validate_input(command='track')
async def track_command(message):
    output = message.output
    print(output)
    if len(output.split()) == 1:
        print(output)
    await message.answer(output)


@dp.message_handler()
async def echo_all(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        sentry_sdk.capture_exception(e)

