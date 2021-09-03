"""
For managing an ADC thing
It essentially acts as a collection of sensors
The board settings are configured via a config file
But the calling code can register sensors
"""

import logging

from .. import MECSConfigError, MECSHardwareError
from .ADCPi import ABEHelpers, ADCPi

log = logging.getLogger(__name__)

class ADCError(MECSConfigError): pass

class ADCThing:
    def __init__(self, conf):
        self.impedance = conf.getfloat('input_impedance')
        self.bit_rate = conf['bit_rate']
        self.sensors = {}

        bus = ABEHelpers().get_smbus()
        if bus:
            self.adc = ADCPi(bus, rate=self.bit_rate)
        else:
            self.adc = None
            log.warning(f"ABEHelpers().get_smbus() returned {bus}")
            # raise MECSHardwareError("No ADC bus detected")

    def register(self, label, conf):
        self.sensors[label] = ADCSensor(label, conf, self.impedance)


    def getSample(self, channel, N):
        self.adc.set_conversion_mode(1)
        readings = [self.adc.read_voltage(channel) for i in range(N)]
        self.adc.set_conversion_mode(0)
        return readings

    def getAverageSample(self, channel, N):
        return sum(self.getSample(channel, N))/N

    def calibrate(self, conf, N):
        for label, sensor in self.sensors.items():
            if sensor.type == "current":
                sensor.zero_point = self.getAverageSample(sensor.channel, N)
                log.info(f"Calibrating zero_point for [{label}]")
                conf.set(sensor.label, "zero_point", str(sensor.zero_point))
        return conf


    def readings(self):
        if not self.adc:
            return {label: None for label in self.sensors}
        return {
            sensor.label: sensor.correct(self.adc.read_voltage(sensor.channel))
            for sensor in self.sensors.values()
        }

    def __repr__(self):
        tab = ",\n\t"
        return f"ADCThing(impedance={self.impedance}, bit_rate={self.bit_rate}, \n\t{tab.join(str(s) for s in self.sensors.values())}\n)"

    def __str__(self):
        sep = "\n    "
        return f"""
ADCThing(impedance={self.impedance}, bit_rate={self.bit_rate})
    {sep.join(str(s) for s in self.sensors.values())}
"""

class ADCSensor:
    def __init__(self, label, calibration, impedance):
        self.label = label
        self.channel = calibration.getint('channel')
        self.type = calibration.get('type')
        self.zero_point = calibration.getfloat('zero_point')
        if self.type not in ["voltage", "current"]:
            raise ADCError(f"unsupported type: {self.type}")
        if self.type == "voltage":
            resistance = calibration.getfloat('resistance')
            self.sensitivity = (impedance + resistance) / impedance
        elif self.type == "current":
            self.sensitivity = 1000 / calibration.getfloat('milliVoltPerAmp')
        log.debug(f"{self} registered")

    def correct(self, raw):
        return (raw - self.zero_point) * self.sensitivity

    def __repr__(self):
        if self.type == "current":
            return f"ADCSensor({self.label!r}, channel={self.channel!r}, type={self.type!r}, zero_point={self.zero_point})"
        else:
            return f"ADCSensor({self.label!r}, channel={self.channel!r}, type={self.type!r})"
