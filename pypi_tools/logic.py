import aioredis
import os
import xml.etree.ElementTree as ET
import re

redis_host = f"redis://{os.environ.get('REDIS_HOST')}"

def parse_xml_file_with_version(_text, nodev=False):
    """parse f"https://pypi.org/rss/project/{package_name}/releases.xml to get list of package releases"""
    root = ET.fromstring(_text)
    versions = {}
    for channel in root:
        for item in channel:
            version = None
            date_ = None
            for elem in item:
                if elem.tag == 'title':
                    version = elem.text
                elif elem.tag == 'pubDate':
                    date_ = elem.text
            if version:
                if nodev:
                    if not re.search('[a-zA-Z]', version):
                        versions[version] = date_
                else:
                    versions[version] = date_
    return versions


async def remove_track_for_package(key):
    pool = await aioredis.create_redis_pool(redis_host)
    with await pool as redis:
        key_in_redis = await redis.get(key)
        if key_in_redis is None:
            output = f"You did not track package <b>{key.split(':')[1]} </b>\n\n" \
                    f"<i>If you want start track package releases - use command /track package_name</i>"    
        else:
            await redis.delete(key)
            output = f"Package <b>{key.split(':')[1]}</b> was removed from your track. \n" \
                    f"You will not get information about new releases"
        return output
