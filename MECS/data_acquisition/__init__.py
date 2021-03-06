import logging
import os
from configparser import ConfigParser, NoOptionError
from datetime import datetime
import time
import math

from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import KernelModuleLoadError, NoSensorFoundError, ResetValueError, SensorNotReadyError

from .. import MECSConfigError, MECSHardwareError
from .ADCPi import ABEHelpers, ADCPi
from .sds011.SDS011 import SDS011, serial
from .INA3221 import SDL_Pi_INA3221
from .PanasonicSNGCJA5.sngcja5 import SNGCJA5

log = logging.getLogger(__name__)

class UnknownType(MECSConfigError): pass

# TODO: test with numpy for speed improvements
def rms(readings):
    """A utility function for calculating RMS values for an array"""
    mean_reading = sum(readings) / len(readings)
    squared_diff = [(r-mean_reading)**2 for r in readings]
    mean_squared = sum(squared_diff) / len(squared_diff)
    return math.sqrt(mean_squared)


class ADCSensor:
    def __init__(self, label, calibration, impedance):
        self.label = label
        self.channel = calibration.getint('channel')
        self.type = calibration.get('type')
        self.zero_point = calibration.getfloat('zero_point')
        if self.type == "voltage":
            resistance = calibration.getfloat('resistance')
            self.sensitivity = (impedance + resistance) / impedance
        elif self.type == "current":
            self.sensitivity = 1000 / calibration.getfloat('milliVoltPerAmp')
        else:
            raise UnknownType(f"{self} type should be 'current' or 'voltage' only")
        log.debug(f"{self} registered")

    def correct(self, raw):
        return (raw - self.zero_point) * self.sensitivity

    def __repr__(self):
        if self.type == "current":
            return f"ADCSensor({self.label!r}, channel={self.channel!r}, type={self.type!r}, zero_point={self.zero_point})"
        else:
            return f"ADCSensor({self.label!r}, channel={self.channel!r}, type={self.type!r})"

class INA3221Config:
    def __init__(self, label, channel, type):
        self.callables = {
            "current": self._current,
            "busVoltage": self._busVoltage,
            "shuntVoltage": self._shuntVoltage
        }
        if type not in ["current", "busVoltage", "shuntVoltage"]:
            raise UnknownType(type)
        self.label = label
        self.channel = channel
        self.type = type
        log.debug(f"{self} registered")


    def _busVoltage(self, sensor):
        busvoltage = sensor.getBusVoltage_V(self.channel)
        return busvoltage

    def _shuntVoltage(self, sensor):
        shuntvoltage = sensor.getShuntVoltage_mV(self.channel) / 1000
        return shuntvoltage

    def _current(self, sensor):
        return sensor.getCurrent_mA(self.channel) / 1000

    def read(self, sensor):
        return self.callables[self.type](sensor) if sensor else None

    def __repr__(self):
        return f"INA3221Config({self.label!r}, channel={self.channel!r}, type={self.type!r})"


class MECSBoard:
    """
    Class representing the MECS board configuration
    Handles grabbing data from sensors and performing necessary adjustments
    """
    def __init__(self, bit_rate, input_impedance, calibration_file_path):
        """Initialise the instance with a calibration file
        Calculates all the constants
        """
        if not os.path.exists(calibration_file_path):
            raise MECSConfigError(f"configuration file {calibration_file_path} not found")
        log.info(f"loading calibration data from {calibration_file_path}")
        self.config = ConfigParser()
        self.config.read(calibration_file_path)

        # Initialise the analogue to digital converter interface
        bus = ABEHelpers().get_smbus()
        if not bus:
            log.warning(f"ABEHelpers().get_smbus() returned {bus}")
            raise MECSHardwareError("No ADC bus detected")

        self.adc = ADCPi(bus, rate=bit_rate)

        try:
            self.INA3221 = SDL_Pi_INA3221()
            log.debug("Added INA3221 sensor")
        except OSError as exc:
            log.warn("Cannot communicate with INA3221, is it powered and connected to serial?")
            log.exception(exc)
            self.INA3221 = None

        # ADCPi calibration information
        self.analogue_sensors = {section: ADCSensor(section, self.config[section], input_impedance) for section in self.config if self.config.get(section, 'protocol', fallback=False) == "adc"}

        # INA3221 calibration information
        self.power_sensors = {section: INA3221Config(section, self.config[section].getint('channel'), self.config[section]['type']) for section in self.config if self.config.get(section, 'protocol', fallback=False) == "INA3221"}

        # Initialise the SDS011 air particulate density sensor.
        try:
            if self.config['particulates'].get('type',fallback=False) == 'SNGCJA5':
                self.particulate_sensor = SNGCJA5(i2c_bus_no=1,logger='MECS')
                log.debug(f"Add SNGCJA5 particulate sensor")
            else:
                log.warn(f"Unknown particulate sensor type specified : {self.config['particulates'].get('type',fallback=False)}")
        except serial.serialutil.SerialException as exc:
            log.error(exc)
            log.warning(f"Particulate sensor not found")
            self.particulate_sensor = None

        try:
            self.temp_sensor = W1ThermSensor()
        except KernelModuleLoadError as exc:
            log.error(exc)
            log.warning(f"Either the kernel does not have the required one wire modules, or they can't be loaded : temp sensor unavailable")
            self.temp_sensor = None
        except NoSensorFoundError as exc:
            log.error(exc)
            log.warning(f"No temp sensor found on the gpio one-wire interface")
            self.temp_sensor = None

    ####
    # Code snippet added by Henrik 2021-05-28
    # Code snippet modified by Henrik 2021-06-02
    # This function converts LM35 voltage readings to temperature
    # Output voltage signal is given by 10mV/C*T
    ####
    def getLM35(self, channel):
        mVolts = self.adc.read_voltage(channel)
        lm35_scale_factor = 10 # Linear scale factor 10mV/C
        temp = (mVolts/lm35_scale_factor) * 1000
        return round(temp, 3)

    def get_temperature(self):
        if not self.temp_sensor:
            return None
        try:
            return round(self.temp_sensor.get_temperature(), 2)
        except (ResetValueError, SensorNotReadyError) as exc:
            log.error(exc)
            log.warn(f"Sensor is not ready to be read")
            return None


    def get_particulates(self):
        if not self.particulate_sensor:
            return {}
        return self.particulate_sensor.get_mass_density_data() # in ug/m3
        #counts = self.particulate_sensor.get_count_data()# Units in counts/sec according to documentation.  Unclear utility

    def get_power(self):
        return {
            sensor.label: sensor.read(self.INA3221)
            for sensor in self.power_sensors.values()
        }

    def getSample(self, channel, N):
        self.adc.set_conversion_mode(1)
        readings = [self.adc.read_voltage(channel) for i in range(N)]
        self.adc.set_conversion_mode(0)
        return readings


    def getRMSSample(self, channel, N):
        return rms(self.getSample(channel, N))


    def getAverageSample(self, channel, N):
        return sum(self.getSample(channel, N))/N


    def calibrate(self, N):
        new_conf = self.config
        for label, sensor in self.analogue_sensors.items():
            if sensor.type == "current":
                sensor.zero_point = self.getAverageSample(sensor.channel, N)
                log.info(f"Calibrating zero_point: {sensor}")
                new_conf.set(sensor.label, "zero_point", str(sensor.zero_point))
        return new_conf

    def analogue_reading(self, label):
        sensor = self.analogue_sensors[label]
        return sensor.correct(self.adc.read_voltage(sensor.channel))

    def readings(self):
        """Bring all the data together into a neat packet with a timestamp"""
        result = {
            sensor.label: sensor.correct(self.adc.read_voltage(sensor.channel))
            for sensor in self.analogue_sensors.values()
        }
        result.update(self.get_particulates())

        result['temperature'] = self.get_temperature()

        result.update(self.get_power());

        return {
            "dt": datetime.utcnow(),
            "data": result
        }
