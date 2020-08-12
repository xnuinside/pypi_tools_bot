import os
import logging
import sentry_sdk
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, timedelta
from pypi_tools.logic import remove_track_for_package
import pypi_tools.data as d
from pypi_tools.helpers import validate_input
import pypi_tools.vizualizer as v
import pypi_tools.readme as r
import asyncio
import aioredis


logging.basicConfig(level=logging.INFO)
redis_host = f"redis://{os.environ.get('REDIS_HOST')}"
sentry_sdk.init(os.environ["SENTRY_PATH"])

bot = Bot(token=os.environ["BOT_API_KEY"], parse_mode="html")
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message):
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
        current_date = datetime.now().date()
        data_ = await d.cached_package_downloads_stats(package_name, days, current_date)
        output = d.stats_text(data_, package_name, days)
    await message.answer(output)

@dp.message_handler(lambda message: message.text and (
        '/plot' in message.text.lower() or 'plot:' in message.text.lower()))
@validate_input(command='plot',
                known_sub_commands={'@any_number': lambda num: num})
async def send_package_stats_with_graph(message):
    output = message.output
    sub_command = message.sub_command or 5
    if len(output.split()) == 1:
        days = sub_command
        package_name = output
        current_date = datetime.now().date()
        data_ = await d.cached_package_downloads_stats(package_name, days, current_date)
        output = d.stats_text(data_, package_name, days)   
        temp = 'temp/'
        os.makedirs(temp, exist_ok=True)
        # for pandas range
        start_date = current_date - timedelta(days=2)
        file_name = f'{temp}/{package_name}:{current_date - timedelta(days=1)}:{days}.png'
        if not os.path.isfile(file_name):
            file_name = v.generate_graph(start_date, [item for _, item in data_.items()][::-1], file_name)
        file_ = types.InputFile(file_name)
    await message.answer(output)
    await message.answer_photo(file_)

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

track_sub_commands = {'stop': lambda key: remove_track_for_package(key), 
                      'nodev': 'nodev'}

@dp.message_handler(commands=['track', 'track:stop', 'track:nodev'])
@validate_input(command='track',
                known_sub_commands=track_sub_commands,
                additional_error="Or use with sub-command to stop track a package releases"
                                 "/track:stop aiohttp")
async def track_command(message):
    """ handler to react on /track command and it sub-commands"""
    redis = await aioredis.create_redis(redis_host)
    output = message.output
    sub_command = message.sub_command
    if len(output.split()) == 1:
        package_name = output
        chat_id = str(message.chat.id)
        key = chat_id + ":" + package_name
        if sub_command and sub_command != 'nodev':
            output = await sub_command(key)
        else:
            nodev = False
            if sub_command:
                nodev = True
            versions = await d.get_release_list(package_name, nodev)
            if versions is None:
                output = f'Package {package_name} does not exists'
            else:
                current_version = d.get_last_release_version(versions)
                output = f"Current {package_name} version is {current_version} \n" \
                "You will be announced with new version release"
                version = current_version[0]
                if nodev:
                    version = version + ':nodev'
                await redis.set(key, version)
    await message.answer(output)


@dp.message_handler()
async def echo_all(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        sentry_sdk.capture_exception(e)

