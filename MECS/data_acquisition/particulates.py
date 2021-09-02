import logging
from datetime import datetime

from .sds011.SDS011 import SDS011, serial

log = logging.getLogger(__name__)


class SDS011Thing:
    def __init__(self):
        self.sensors = {}

    def register(self, label, conf):
        try:
            sensor = SDS011(conf.get('serial_port'), use_query_mode=True)
            sensor.sleep()                  # Turn it off to avoid draining power
            self.sensors[label] = sensor
        except serial.serialutil.SerialException as exc:
            log.error(exc)
            log.warning(f"Particulate sensor not found at {conf.get('serial_port')}")
            self.sensors[label] = None


    def _toggle_sensor(self, label):
        # This is a classic "turning it off and on again" move
        self.sensors[label].sleep()
        self.sensors[label].sleep(sleep=False)


    def _read_sensor(self, label):
        sensor = self.sensors[label]
        if not sensor:
            return (None, None)
        sensor.sleep(sleep=False)       # Wake the sensor up
        values = sensor.query()         # get the values
        sensor.sleep()                  # put it back to sleep
        return values


    def readings(self):
        result = {}
        for label in self.sensors:
            PM2_5, PM10 = self._read_sensor(label)
            result[f"{label}_PM2.5"] = PM2_5
            result[f"{label}_PM10"] = PM10
        return result


    def __repr__(self):
        labels = ", ".join(self.sensors)
        return f"SDS011Thing({labels})"
