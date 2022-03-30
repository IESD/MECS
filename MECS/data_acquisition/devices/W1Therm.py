import os
import logging

os.environ['W1THERMSENSOR_NO_KERNEL_MODULE'] = '1'

from w1thermsensor.errors import KernelModuleLoadError, NoSensorFoundError, ResetValueError, SensorNotReadyError
from w1thermsensor import W1ThermSensor, load_kernel_modules

from ... import MECSConfigError, MECSHardwareError

log = logging.getLogger(__name__)

class W1ThermError(MECSConfigError): pass

class W1ThermDevice:
    def __init__(self, hardware_required=True, **kwargs):
        self.label = kwargs['label']
        try:
            load_kernel_modules()
            self.sensor = W1ThermSensor()
        except KernelModuleLoadError as exc:
            log.error(exc)
            log.warning(f"Either the kernel does not have the required one wire modules, or they can't be loaded : temp sensor unavailable")
            self.sensor = None
        except NoSensorFoundError as exc:
            log.error(exc)
            log.warning(f"No temp sensor found on the gpio one-wire interface")
            self.sensor = None
        except FileNotFoundError as exc:
            log.error(exc)
            log.warning(f"There's something wrong here - possibly run with NO_KERNAL_MODULE?")
            self.sensor = None
        if hardware_required and not self.sensor:
            raise MECSHardwareError("Can't access w1therm sensor")
        log.debug(f"{self} created")


    def _read(self):
        if not self.sensor:
            return None
        try:
            return round(self.sensor.get_temperature(), 2)
        except (ResetValueError, SensorNotReadyError) as exc:
            log.error(exc)
            log.warn(f"Sensor is not ready to be read")
            return None

    def read(self):
        yield self.label, self._read()    

    def readings(self):
        return dict(self.read())

    def __repr__(self):
        return f"W1ThermDevice({self.label!r})"