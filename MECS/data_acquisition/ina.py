import logging

from .INA3221 import SDL_Pi_INA3221

log = logging.getLogger(__name__)

class INA3221Thing:
    def __init__(self):
        self.calibrations = {}
        try:
            self.sensor = SDL_Pi_INA3221()
        except PermissionError:
            log.warning("Couldn't access INA3221")
            self.sensor = None

    def register(self, label, conf):
        self.calibrations[label] = INA3221Config(label, conf)

    def readings(self):
        if not self.sensor:
            return {}
        return {
            cal.label: cal.read(self.sensor)
            for cal in self.calibrations.values()
        }

    def __repr__(self):
        tab = ",\n\t"
        return f"INA3221Board(\n\t{tab.join(str(s) for s in self.calibrations.values())}\n)"


    def __str__(self):
        sep = "\n    "
        return f"""
INA3221
    {sep.join(str(s) for s in self.calibrations.values())}
"""

class INA3221Config:
    def __init__(self, label, conf):
        self.channel = conf.getint('channel')
        self.label = label
        self.type = conf.get('type')
        if self.type not in ["current", "busVoltage", "shuntVoltage"]:
            raise UnknownType(type)
        self.callables = {
            "current": self._current,
            "busVoltage": self._busVoltage,
            "shuntVoltage": self._shuntVoltage
        }

    def _busVoltage(self, sensor):
        return sensor.getBusVoltage_V(self.channel)

    def _shuntVoltage(self, sensor):
        return sensor.getShuntVoltage_mV(self.channel) / 1000

    def _current(self, sensor):
        return sensor.getCurrent_mA(self.channel) / 1000

    def read(self, sensor):
        return self.callables[self.type](sensor) if sensor else None

    def __repr__(self):
        return f"INA3221Config({self.label!r}, channel={self.channel!r}, type={self.type!r})"
