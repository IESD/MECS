import logging
import os
from configparser import ConfigParser, NoOptionError
from datetime import datetime
import math

from .ADCPi import ABEHelpers, ADCPi
from .sds011.SDS011 import SDS011, serial

log = logging.getLogger(__name__)

# proper constants
kelvinToCentigrade = 273

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
        self.zero_point = calibration.getfloat('zero_point')
        if calibration.get('type') == "voltage":
            resistance = calibration.getfloat('resistance')
            self.sensitivity = (impedance + resistance) / resistance
        else:
            self.sensitivity = 1000 / calibration.getfloat('milliVoltPerAmp')


    def correct(self, raw):
        return (raw - self.zero_point) * self.sensitivity



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
            log.error(f"configuration file {calibration_file_path} not found")
            exit(1)
        log.info(f"loading calibration data from {calibration_file_path}")
        self.config = ConfigParser()
        self.config.read(calibration_file_path)

        # Initialise the analogue to digital converter interface
        bus = ABEHelpers().get_smbus()
        if not bus:
            log.error("ABEHelpers().get_smbus() returned None")
            exit(1)
        self.adc = ADCPi(bus, rate=bit_rate)

        # ADCPi calibration information
        self.analogue_sensors = [ADCSensor(section, self.config[section], input_impedance) for section in self.config if self.config.get(section, 'protocol', fallback=False) == "adc"]

        # Initialise the SDS011 air particulate density sensor.
        try:
            self.particulate_sensor = SDS011(self.config['SDS011'].get('serial_port'), use_query_mode=True)
            self.particulate_sensor.sleep() # Turn it off (to avoid draining power?)
        except serial.serialutil.SerialException as exc:
            log.warning(f"Particulate sensor not found at {self.config['SDS011'].get('serial_port')}")
            log.error(exc)
            self.particulate_sensor = None


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


    def getParticulates(self):
        if not self.particulate_sensor:
            return (None, None)

        # Wake the sensor up
        self.particulate_sensor.sleep(sleep=False)

        # possibly wait a moment before using it?
        # time.sleep(0.05)

        # or can we do this to read the status?
        # while(self.particulate_sensor.sleep(read=False, sleep=False)):
        #     time.sleep(0.01)

        for attempt in range(10): # could be while((now - start_timestamp) < timeout)
            values = self.particulate_sensor.query()
            if bool(values) and len(values) == 2:
                return values

            # This is a classic "turning it off and on again" move
            self.particulate_sensor.sleep()
            self.particulate_sensor.sleep(sleep=False)

            # Can we afford to wait five seconds each try?
            # This adds up to a maximum of 50 seconds!
            # Alternative is get a timestamp and while((now - start_timestamp) < timeout)
            time.sleep(5)

        # Put the sensor back to sleep before returning
        self.particulate_sensor.sleep()

        # we should check if we can pass recognisably invalid data through to the server
        return (None, None)


    def getRMSvoltage(self, channel, N):
        self.adc.set_conversion_mode(1)
        readings = [self.adc.read_voltage(channel) for i in range(N)]
        self.adc.set_conversion_mode(0)
        return rms(readings)


    def readings(self):
        """Bring all the data together into a neat packet with a timestamp"""
        result = {
            a.label: a.correct(self.adc.read_voltage(a.channel))
            for a in self.analogue_sensors
        }
        PM2_5, PM10 = self.getParticulates()
        result['PM2.5'] = PM2_5
        result['PM10'] = PM10
        result['temperature'] = None
        return {
            "dt": datetime.utcnow(),
            "data": result
        }
