import logging

from ... import MECSConfigError, MECSHardwareError
from ..sds011.SDS011 import SDS011, serial


log = logging.getLogger(__name__)

class SDS011Error(MECSConfigError): pass


class SDS011Device:
    def __init__(self, hardware_required=True, **kwargs):
        try:
            self.label = kwargs['label']
            self.port = kwargs['serial_port']
        except KeyError as e:
            raise SDS011Error(f"[{e}] missing")

        try:
            self.sensor = SDS011(self.port, use_query_mode=True)
            self.sensor.sleep()                  # Turn it off to avoid draining power
        except serial.serialutil.SerialException as exc:
            log.error(exc)
            log.warning(f"SDS011 particulate sensor not found at {self.port}")
            self.sensor = None
            if hardware_required:
                raise MECSHardwareError(f"SDS011 particulate sensor not found at {self.port}")


        log.debug(f"{self} created")


    def _toggle_sensor(self, label):
        """This is a classic "turning it off and on again" move"""
        self.sensor.sleep()
        self.sensor.sleep(sleep=False)


    def read(self):
        """This reads the sensor and yields a formatted output with appropriate labels"""
        PM2_5, PM10 = (None, None)               # default values
        if self.sensor:
            self.sensor.sleep(sleep=False)       # Wake the sensor up
            PM2_5, PM10 = self.sensor.query()    # get the values
            self.sensor.sleep()                  # put it back to sleep

        yield f"{self.label}_PM2.5", PM2_5       # yield PM2.5
        yield f"{self.label}_PM10", PM10         # yield PM10

    def readings(self):
        return dict(self.read())

    def __repr__(self):
        return f"SDS011Device({self.label!r}, {self.port!r})"
