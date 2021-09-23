"""
The MECS board is a high-level interface for configuring and accessing the MECS hardware
This is the entry point for normal usage of the MECS system.
"""

import logging
from datetime import datetime

from .. import MECSConfigError

from .devices import (
    ADCDevice,
    INA3221Device,
    SNGCJA5Device,
    SDS011Device,
    W1ThermDevice
)

log = logging.getLogger(__name__)

known_devices = {
    # These string keys are the devices that can be specified in the config dictionary
    "ADCPi": ADCDevice,
    "INA3221": INA3221Device,
    "SNGCJA5": SNGCJA5Device,
    "SDS011": SDS011Device,
    "W1THERM": W1ThermDevice,
}

class MECSBoard:
    def __init__(self, hardware_required=True, **kwargs):
        """
        Ingest configuration data
        Raise a configuration error if anything goes wrong
        """
        self.devices = {}
        for key, config in kwargs.items():
            if not isinstance(config, dict):
                raise MECSConfigError(f"section [{key}] must contain a dictionary")
            if "device" not in config:
                raise MECSConfigError(f"section [{key}] must specify a 'device' from [{', '.join(known_devices.keys())}]")
            device = config.pop('device')
            if device not in known_devices:
                raise MECSConfigError(f"section [{key}] includes unsupported device '{device}', try one of [{', '.join(known_devices.keys())}]")
            try:
                self.devices[key] = known_devices[device](hardware_required, **config)
            except MECSConfigError as e:
                raise MECSConfigError(f"[{key}]{e}")
            except TypeError as e:
                raise MECSConfigError(f"[{key}]: {e}")

        labels = set()
        for device_label, device in self.devices.items():
            for data_label, _ in device.read():
                if data_label in labels:
                    raise MECSConfigError(f"[{device_label!r}] produced duplicate label: {data_label!r}")
                labels.add(data_label)

    def calibrate(self, N):
        for label, device in self.devices.items():
            try:
                device.calibrate(N)
                log.info(f"calibrated device {label!r}")
                yield label, device.config()
            except AttributeError:
                log.debug(f"device {label!r} has no calibrate method")

    def read(self):
        """All the readings"""
        for _, device in self.devices.items():
            for label, value in device.read():
                yield label, value

    def readings(self):
        """Bring all the data together into a neat packet with a timestamp"""
        data = {k: v for k, v in self.read()}
        return {
            "dt": datetime.utcnow(),
            "data": data
        }

    def config(self):
        return {label: module.config() for label, module in self.registerables.items()}

    def __repr__(self):
        return f"MECSBoard({', '.join(self.devices.keys())})"
