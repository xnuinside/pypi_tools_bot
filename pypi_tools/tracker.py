import logging
import os
import asyncio
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from dotenv import load_dotenv
from pypi_tools import data as d
import aioredis

load_dotenv()
redis_host = f"redis://{os.environ.get('REDIS_HOST')}"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
bot = Bot(token=os.environ["BOT_API_KEY"], parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def get_ids_with_keys():
    """
    Return list of chat ids with packages

    In this example returns some random ID's
    """
    pool = await aioredis.create_redis_pool(redis_host)
    with await pool as redis:
        keys = redis.iscan(match=r'[0-9]*')
        ids_parsed = defaultdict(list)
        async for key in keys:
            key = key.decode('utf-8')
            splitted_key = key.split(':')
            id_ = splitted_key[0]
            # it's needed because we will need to get version by key from redis
            ids_parsed[id_].append(key)
        for id_, packages_keys in ids_parsed.items():
            yield id_, packages_keys

async def compare_new_version(package_key):
    """ check exist new version of package or not """
    package_name = package_key.split(":")[1]
    nodev = False
    pool = await aioredis.create_redis_pool(redis_host)
    with await pool as redis:
        current_version = (await redis.get(package_key)).decode('utf-8')

        if ':nodev' in current_version:
            nodev = True
            current_version = current_version.split(':nodev')[0]
        versions = await d.get_release_list(package_name, nodev)
        last_version = d.get_last_release_version(versions)[0]
        if last_version != current_version:
            return last_version, nodev
    return False, nodev

async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def find_new_version_and_send_message(user_id, package_key):
    pool = await aioredis.create_redis_pool(redis_host)
    with await pool as redis:
        package_name = package_key.split(":")[1]
        new_version, nodev = await compare_new_version(package_key)
        if new_version is not False:
            await send_message(user_id, 
                f'New version of <b>{package_name}</b> is released \n'
                f'New version: {new_version} \n\n'
                f'Release link: https://pypi.org/project/{package_name}/{new_version}/ \n\n'
                f'<i>If you don\'t want track package releases anymore use command: /track:stop gino-admin</i>')
            if nodev:
                new_version = new_version + ":nodev"
            await redis.set(package_key, new_version)


async def tracker() -> int:
    """
    Sent anounce about release if new version was released
    :return: Count of messages
    """
    async for user_id, packages_keys in get_ids_with_keys():
        asyncio.gather(*[find_new_version_and_send_message(user_id, package_key) for package_key in packages_keys])
    await asyncio.sleep(.05)
