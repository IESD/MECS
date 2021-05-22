"""
grab data and write it to files

here we generate one file per minute
Obviously we want to minimise the data kept in memory
And writing to disk regularly minimises potential data loss
There is a balance, we might be happy to gather an hour of data before writing to a file.
"""

import logging
import signal
from time import sleep

import pandas as pd

from .get_input import raw_readings as fake_readings

log = logging.getLogger(__name__)

# adapted from https://stackoverflow.com/a/31464349/1083707
# This just allws us to log the end of data generation
class GracefulKiller:
    def __init__(self):
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully1)
        signal.signal(signal.SIGTERM, self.exit_gracefully2)

    def exit_gracefully1(self,signum, frame):
        log.info("PROCESS INTERRUPTED!")
        self.kill_now = True

    def exit_gracefully2(self,signum, frame):
        log.info("PROCESS TERMINATED!")
        self.kill_now = True


def aggregated_minutely_readings(fake, delay=1):
    if not fake:
        from ..data_acquisition.sensors_api import raw_readings

    killer = GracefulKiller()
    data = []
    last_minute = fake_readings()['dt'].replace(second=0, microsecond=0)
    log.info(f"Initialising data collection at {last_minute}")
    while not killer.kill_now:
        readings = fake_readings() if fake else raw_readings()
        log.debug(f"reading taken at {readings['dt']}")
        if last_minute != readings['dt'].replace(second=0, microsecond=0):
            result = pd.DataFrame(data).mean().to_dict()
            result['dt'] = last_minute
            log.debug(f"minutely output: {result}")
            yield result
            data = []
            last_minute = readings['dt'].replace(second=0, microsecond=0)
        data.append(readings['data'])
        sleep(delay)
    log.info("Infinite loop was ended gracefully :)")
