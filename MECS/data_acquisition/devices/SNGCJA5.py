import logging

import serial

from ..PanasonicSNGCJA5.sngcja5 import SNGCJA5


log = logging.getLogger(__name__)

class SNGCJA5Device:
    def __init__(self, hardware_required=True, **kwargs):
        self.label = kwargs['label']
        self.i2c_bus_no = kwargs['i2c_bus_no']

        try:
            self.sensor = SNGCJA5(i2c_bus_no=self.i2c_bus_no,logger=__name__)
        except serial.serialutil.SerialException as exc:
            log.error(exc)
            log.warning(f"Particulate sensor not found")
            self.sensor = None
        except PermissionError as e:
            log.error(e)
            log.warning(f"Particulate sensor not found")
            self.sensor = None

        log.debug(f"{self} created")

    def read(self):
        if self.sensor:
            for label, value in self.sensor.get_mass_density_data():
                yield f"{self.label}_{label}", value
        else:
            yield f"{self.label}_PM1.0", None
            yield f"{self.label}_PM2.5", None
            yield f"{self.label}_PM10", None

    def readings(self):
        return dict(self.read())

    def __repr__(self):
        return f"SNGCJA5Device({self.label!r}, i2c_bus_no={self.i2c_bus_no!r})"
