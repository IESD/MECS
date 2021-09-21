"""
For managing an INA3221 thing
"""

import logging

from ... import MECSConfigError, MECSHardwareError
from ..INA3221 import SDL_Pi_INA3221

log = logging.getLogger(__name__)

class INA3221Error(MECSConfigError): pass

class INA3221Device:
    def __init__(self, hardware_required=True, **kwargs):
        """
        Ingest configuration data
        Raise MECSConfigError if anything is wrong
        """
        try:
            self.device = SDL_Pi_INA3221()
        except PermissionError:
            log.warning("Couldn't access INA3221")
            self.device = None
            if hardware_required:
                raise MECSHardwareError("Couldn't access INA3221 device")

        data_points = kwargs['data_points']

        self.data_points = {}
        for key, config in data_points.items():
            self.register(key, config)

        log.debug(f"{self} created")

    def register(self, label, conf):
        self.data_points[label] = INA3221DataPoint(**conf)

    def read(self):
        for label, dp in self.data_points.items():
            yield label, dp.read(self.device)
    
    def readings(self):
        return dict(self.read())

    def __repr__(self):
        data_points = ", ".join([f"{data_point.type}_{data_point.channel}: {label!r}" for label, data_point in self.data_points.items()])
        return f"INA3221({data_points})"

VALID_TYPES = ["current", "busVoltage", "shuntVoltage"]

class INA3221DataPoint:
    def __init__(self, **kwargs):
        self.channel = kwargs['channel']
        self.type = kwargs['type']
        if self.type not in VALID_TYPES:
            raise INA3221Error(f"Unknown type {self.type!r} (try one of {VALID_TYPES}")
        self.callables = {
            "current": self._current,
            "busVoltage": self._busVoltage,
            "shuntVoltage": self._shuntVoltage
        }

        log.debug(f"{self} created")


    def _busVoltage(self, sensor):
        return sensor.getBusVoltage_V(self.channel)

    def _shuntVoltage(self, sensor):
        return sensor.getShuntVoltage_mV(self.channel) / 1000

    def _current(self, sensor):
        return sensor.getCurrent_mA(self.channel) / 1000

    def read(self, sensor):
        return self.callables[self.type](sensor) if sensor else None

    def __repr__(self):
        return f"INA3221DataPoint(channel={self.channel!r}, type={self.type!r})"

