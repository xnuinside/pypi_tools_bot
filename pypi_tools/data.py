from google.cloud import bigquery
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv
from pypi_tools.logic import parse_xml_file_with_version
from concurrent.futures import ThreadPoolExecutor
import asyncio
from random import choice

load_dotenv()
client = bigquery.Client()


def bq_get_downloads_stats_for_package(package_name, date_):
    formatted_date_ = date_.replace('-', '')
    query_job = client.query(
        f"SELECT count(timestamp) as downloads, {formatted_date_} as date FROM `the-psf.pypi.downloads{formatted_date_}` "
        f"WHERE file.project=\'{package_name}\'")
    return query_job


def bq_get_unique_packages_downloaded_for_yesterday():
    query_job = client.query(
        f"SELECT count(distinct(file.project)) as packages_number FROM "
        f"`the-psf.pypi.downloads{(datetime.now().date() - timedelta(days=1)).isoformat().replace('-', '')}`;")

    results = query_job.result()
    results = [row for row in results]
    return results[-1].packages_number


def bq_get_random_packages_downloaded_for_yesterday():
    query_job = client.query(
        f"SELECT distinct(file.project) as package_name FROM "
        f"`the-psf.pypi.downloads{(datetime.now().date() - timedelta(days=1)).isoformat().replace('-', '')}` "
        f"WHERE RAND() < 10/164656895;")

    results = query_job.result()
    results = [row.package_name for row in results]
    return results


async def get_random_package():
    packages = bq_get_random_packages_downloaded_for_yesterday()
    random_name = choice(packages)
    return await request_package_info_from_pypi(random_name)


async def request_package_info_from_pypi(package_name, detailed=False):
    result = await httpx.get(f"https://pypi.org/pypi/{package_name}/json")
    if result.status_code == 200:
        result = result.json()
        info = result["info"]
        output = f'<b>Package name:</b> {package_name}\n' \
                 f'<b>Latest version:</b> {info["version"]} | <b>Python version:</b> {info["requires_python"]}\n' \
                 f'<b>Homepage:</b> {info["project_urls"]["Homepage"]}\n'\
                 f'<b>PyPi url:</b> https://pypi.org/project/{package_name}\n'

        if detailed:
            latest_release_date = None
            if len(result["releases"][info["version"]]) > 0:
                last_release = result["releases"][info["version"]][0]
                latest_release_date = last_release["upload_time"].split("T")[0]
            output += f'<b>Short description:</b> {info["summary"]}\n' \
                      f'<b>Latest release date:</b> {latest_release_date}\n' \
                      f'<b>Author:</b> {info["author"]}\n'
    else:
        output = f"Package {package_name} does not exist on PyPi"
    return output


async def get_release_list(package_name):
    result = await httpx.get(f"https://pypi.org/rss/project/{package_name}/releases.xml")
    executor = ThreadPoolExecutor(max_workers=1)
    loop = asyncio.get_event_loop()
    versions = await loop.run_in_executor(executor, parse_xml_file_with_version, result.text)
    return versions


def get_last_release_version(versions):
    return list(versions.items())[0]
