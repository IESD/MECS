"""
For managing an ADC device
Most of the code is error handling
The key things are to create the sensors and calculate the readings correctly
"""

import logging

from ... import MECSConfigError, MECSHardwareError
from ..ADCPi import ABEHelpers, ADCPi

log = logging.getLogger(__name__)

class ADCError(MECSConfigError): pass

class ADCDevice:
    def __init__(self, hardware_required=True, **kwargs):
        """
        Ingest configuration data
        Raise MECSConfigError if anything is wrong
        """
        try:
            input_impedance = kwargs['input_impedance']
            bit_rate = kwargs['bit_rate']
            sensors = kwargs['sensors']
        except KeyError as e:
            raise ADCError(f"Missing parameter: {e}")

        try:
            self.input_impedance = float(input_impedance)
        except ValueError as e:
            raise ADCError(f"input_impedance: {input_impedance!r} must be a number")

        try:
            self.bit_rate = int(bit_rate)
        except ValueError as e:
            raise ADCError(f"bit_rate: {bit_rate!r} must be an integer")

        if not isinstance(sensors, dict):
            raise ADCError("'sensors' must be a dictionary")

        for k, v in sensors.items():
            if not isinstance(v, dict):
                raise ADCError(f"channel '{k}' must be a dictionary, not '{v}'")

        self.sensors = {}
        for label, conf in sensors.items():
            try:
                self.register(label, conf)
            except ADCError as e:
                raise ADCError(f"channel ['{label}']: {e}")

        bus = ABEHelpers().get_smbus()
        if bus:
            self.adc = ADCPi(bus, rate=self.bit_rate)
        else:
            self.adc = None
            log.warning(f"ABEHelpers().get_smbus() returned {bus}")
            log.error(f"No ADC bus detected")
            if hardware_required:
                raise MECSHardwareError("No ADC bus detected")

        log.debug(f"{self} created")


    def register(self, label, conf):
        self.sensors[label] = ADCSensor(impedance=self.input_impedance, **conf)

    def getSample(self, channel, N):
        if not self.adc:
            return [0 for _ in range(N)]
        self.adc.set_conversion_mode(1)
        readings = [self.adc.read_voltage(channel) for i in range(N)]
        self.adc.set_conversion_mode(0)
        return readings

    def getAverageSample(self, channel, N):
        return sum(self.getSample(channel, N))/N

    def calibrate(self, N):
        """
        for calibration, we don't handle anything except our own sensors
        we yield ALL sensors to the caller for processing
        whether we calibrated them or not
        """
        for label, sensor in self.sensors.items():
            if sensor.type == "current":
                log.info(f"Calibrating zero_point for [{label}]")
                sensor.zero_point = self.getAverageSample(sensor.channel, N)

    def read(self):
        for label, sensor in self.sensors.items():
            yield label, sensor.reading(self.adc)

    def readings(self):
        return dict(self.read())

    def config(self):
        result = {key: value for key, value in vars(self).items() if key not in ['adc', 'sensors']}
        result["device"] = "ADCPi"
        result['sensors'] = {label: sensor.config() for label, sensor in self.sensors.items()}
        return result

    def __repr__(self):
        sensors = ", ".join([f"ch_{sensor.channel}: {label!r}" for label, sensor in self.sensors.items()])
        return f"ADC({sensors})"

ALLOWED_TYPES = ["voltage", "current"]

class ADCSensor:
    def __init__(self, impedance, **conf):
        try:
            channel = conf['channel']
            type = conf['type']
            zero_point = conf['zero_point']
        except KeyError as e:
            raise ADCError(f"missing required field {e}")

        if type not in ALLOWED_TYPES:
            raise ADCError(f"unsupported type: {type!r} (try one of {ALLOWED_TYPES})")
        try:
            self.channel = int(channel)
        except ValueError:
            raise ADCError(f"channel: {channel!r} (expected integer)")
        try:
            self.zero_point = float(zero_point)
        except ValueError:
            raise ADCError(f"zero_point: {zero_point!r} (expected float)")

        self.type = type

        if type == "voltage":
            try:
                self.resistance = conf['resistance']
            except KeyError as e:
                raise ADCError("voltage sensors require 'resistance' field to be set")
            self.sensitivity = (impedance + self.resistance) / impedance

        elif type == "current":
            try:
                self.milli_volt_per_amp = conf['milliVoltPerAmp']
            except KeyError as e:
                raise ADCError("current sensors require 'milliVoltPerAmp' field to be set")
            self.sensitivity = 1000 / self.milli_volt_per_amp

        log.debug(f"{self} created")

    def reading(self, device):
        if not device:
            return None
        raw = device.read_voltage(self.channel)
        return (raw - self.zero_point) * self.sensitivity

    def config(self):
        """return config data for recreating me"""
        result = {key: value for key, value in vars(self).items() if key != 'sensitivity'}
        if self.type == "current":
            result['milliVoltPerAmp'] = result['milli_volt_per_amp']
            del result['milli_volt_per_amp']
        return result

    def __repr__(self):
        if self.type == "current":
            return f"ADCSensor(channel {self.channel}: {self.type!r}, zero_point: {self.zero_point})"
        else:
            return f"ADCSensor(channel {self.channel}: {self.type!r}, input_resistance: {self.resistance})"