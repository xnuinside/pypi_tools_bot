import asyncio
import os
from async_cron.job import CronJob
from async_cron.schedule import Scheduler
from pypi_tools.tracker import tracker
import sentry_sdk

scheduler = Scheduler(locale="en_US")

#sentry_sdk.init(os.environ["SENTRY_PATH"])

tracker_job = CronJob(
    name='track_packages').every(3).minute.go(tracker)

#scheduler.add_job(tracker_job)

if __name__ == '__main__':
    # Execute broadcaster
    try:
        asyncio.get_event_loop().run_until_complete(scheduler.start())
    except KeyboardInterrupt:
        print('Scheduler exit')
    except Exception as e:
        sentry_sdk.capture_exception(e)