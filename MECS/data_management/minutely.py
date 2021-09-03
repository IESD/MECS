"""
A generator function with an infinite loop.
We grab data continuously, with the given delay
Accumulate readings for a minute
Yield the average data at the end of each minute
"""

import logging
import signal
from time import sleep

import pandas as pd

log = logging.getLogger(__name__)

# adapted from https://stackoverflow.com/a/31464349/1083707
# This just allws us to log the end of data generation
class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.interrupt)
        signal.signal(signal.SIGTERM, self.terminate)

    def interrupt(self,signum, frame):
        log.info("PROCESS INTERRUPTED!")
        self.kill_now = True

    def terminate(self,signum, frame):
        log.info("PROCESS TERMINATED!")
        self.kill_now = True


def aggregated_minutely_readings(get_readings, delay=1):
    killer = GracefulKiller()
    data = []
    last_minute = get_readings()['dt'].replace(second=0, microsecond=0)
    log.info(f"Initialising data collection at {last_minute}")
    while not killer.kill_now:
        readings = get_readings()
        log.debug(f"reading taken at {readings['dt']}")
        if last_minute != readings['dt'].replace(second=0, microsecond=0):
            result = pd.DataFrame(data).mean().to_dict()
            if result['PM1.0']>2000 or result['PM2.5']>2000 or result['PM10']>2000:
                raw = pd.DataFrame(data).to_dict()
                log.debug(f"Dodgy particulate values: 1.0:{raw['PM1.0']};2.5:{raw['PM2.5']};10:{raw['PM10']}")
            result['dt'] = last_minute
            log.debug(f"minutely output: {result}")
            yield result
            data = []
            last_minute = readings['dt'].replace(second=0, microsecond=0)
        data.append(readings['data'])
        sleep(delay)
    log.info("Infinite loop was ended gracefully :)")
