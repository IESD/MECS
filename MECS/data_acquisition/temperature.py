import logging

from w1thermsensor.errors import KernelModuleLoadError, NoSensorFoundError, ResetValueError, SensorNotReadyError
from w1thermsensor import W1ThermSensor

log = logging.getLogger(__name__)

class TemperatureThing:

    def __init__(self):
        self.sensors = {}

    def register(self, label, config):
        try:
            self.sensors[label] = W1ThermSensor()
        except KernelModuleLoadError as exc:
            log.error(exc)
            log.warning(f"Either the kernel does not have the required one wire modules, or they can't be loaded : temp sensor unavailable")
            self.sensors[label] = None
        except NoSensorFoundError as exc:
            log.error(exc)
            log.warning(f"No temp sensor found on the gpio one-wire interface")
            self.sensors[label] = None
        except FileNotFoundError as exc:
            log.error(exc)
            log.warning(f"There's something wrong here - possibly run with NO_KERNAL_MODULE?")
            self.sensors[label] = None


    def _read_sensor(self, label):
        if not self.sensors[label]:
            return None
        try:
            return round(self.sensors[label].get_temperature(), 2)
        except (ResetValueError, SensorNotReadyError) as exc:
            log.error(exc)
            log.warn(f"Sensor is not ready to be read")
            return None


    def readings(self):
        return {
            label: self._read_sensor(label)
            for label in self.sensors
        }
