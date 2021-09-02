"""
The MECS board is a high-level interface for configuring and accessing the MECS hardware
This is the entry point for normal usage of the MECS system.
"""

import logging
from configparser import ConfigParser
from datetime import datetime

from .. import MECSConfigError, MECSHardwareError
from .adc import ADCThing
from .ina import INA3221Thing
from .particulates import SDS011Thing
from .temperature import TemperatureThing

log = logging.getLogger(__name__)

class MECSBoard:
    def __init__(self, conf):
        self.adc = ADCThing(conf["ADCPi"]) # config determines bit_rate and impedance
        self.ina3221 = INA3221Thing()
        self.sds011 = SDS011Thing()
        self.w1_therm = TemperatureThing()
        registerables = {
            "adc": self.adc,
            "INA3221": self.ina3221,
            "SDS011": self.sds011,
            "W1THERM": self.w1_therm
        }
        calibration_file_path = conf['data-acquisition']['calibration_file']
        self.calibration_config = ConfigParser()
        self.calibration_config.read(calibration_file_path)
        for key in self.calibration_config:
            if key == "DEFAULT": continue
            cal = self.calibration_config[key]
            protocol = cal.get("protocol", fallback="unknown")
            try:
                registerables[protocol].register(key, cal)
            except KeyError as ex:
                log.warning(f"ignoring [{key}] unsupported protocol: {protocol}")
            except MECSConfigError as exc:
                log.warning(f"ignoring [{key}]: {exc}")

    def calibrate(self, N):
        log.info("Calibrating ADC current sensors")
        return self.adc.calibrate(self.calibration_config)

    def readings(self):
        """Bring all the data together into a neat packet with a timestamp"""
        data = self.adc.readings()
        data.update(self.ina3221.readings())
        data.update(self.sds011.readings())
        data.update(self.w1_therm.readings())
        return {
            "dt": datetime.utcnow(),
            "data": data
        }

    def __repr__(self):
        return f"MECSBoard(\n{self.adc}, \n{self.ina3221}\n)"

    def __str__(self):
        return f"""
***************************************************************************
MECSBoard configuration
***************************************************************************
{self.adc}
***************************************************************************
{self.ina3221}
***************************************************************************
{self.sds011}
***************************************************************************
        """
