import logging
import os
from configparser import ConfigParser, NoOptionError
from datetime import datetime

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


class MECSBoard:
    """
    Class representing the MECS board configuration
    Handles grabbing data from sensors and performing necessary adjustments
    """
    def __init__(self, calibration_file_path):
        """Initialise the instance with a calibration file
        Calculates all the constants
        """
        if not os.path.exists(calibration_file_path):
            log.error(f"configuration file {calibration_file_path} not found")
            exit(1)
        log.info(f"loading calibration data from {calibration_file_path}")
        self.config = ConfigParser()
        self.config.read(calibration_file_path)

        # Initialise the SDS011 air particulate density sensor.
        try:
            self.particulate_sensor = SDS011(self.config['SDS011'].get('serial_port'), use_query_mode=True)
            self.particulate_sensor.sleep() # Turn it off (to avoid draining power?)
        except serial.serialutil.SerialException as exc:
            log.warning(f"Particulate sensor not found at {self.config['SDS011'].get('serial_port')}")
            log.error(exc)
            self.particulate_sensor = None

        # Initialise the analogue to digital converter interface
        bus = ABEHelpers().get_smbus()
        if not bus:
            log.error("ABEHelpers().get_smbus() returned None")
            exit(1)
        self.adc = ADCPi(bus, rate=self.config['ADCPi'].getint('bit_rate'))


        # ADCPi calibration information
        self.INPUT_IMPEDANCE = self.config['ADCPi'].getint('input_impedance')
        self.R_TOP = self.config['ADCPi'].getint('r_top')
        self.R_BOTTOM = self.config['ADCPi'].getint('r_bottom')
        self.R_EFFECTIVE = self.R_BOTTOM * self.INPUT_IMPEDANCE / (self.R_BOTTOM + self.INPUT_IMPEDANCE)
        # nominally Vcc/2, defaults to 2.5 unless a value is configured
        self.midOffset = self.config['ADCPi'].getint('midOffset', fallback=2.5)
        # default = nominally 100 on the +/-20A version unless a value is configured
        self.milliVoltPerAmp = self.config['ADCPi'].getint('milliVoltPerAmp', fallback=100)

        # Thermistor configuration?
        self.MIN_TEMP = self.config['thermistor'].getint('min_temperature')
        self.MAX_TEMP = self.config['thermistor'].getint('max_temperature')

        self.beta = self.config['thermistor'].getint('beta') # part of thermistor spec
        R0 = self.config['thermistor'].getint('r_0') # 10000 1kOhm at 25 deg C - part of thermistor spec
        T0 = self.config['thermistor'].getint('t_0') + kelvinToCentigrade # convert 25 C to Kelvin

        rBias = self.config['thermistor'].getint('r_bias') # calibrate carefully here
        self.rInf = R0 * math.exp(-self.beta / T0)
        self.rVoltDiv = (rBias*self.INPUT_IMPEDANCE) / (rBias+self.INPUT_IMPEDANCE)


    def getADCVoltage(self, channel):
        raw_voltage = self.adc.read_voltage(channel)
        return raw_voltage * (self.R_TOP + self.R_EFFECTIVE) / self.R_EFFECTIVE


    def getADCCurrent(self, channel):
        raw_voltage = self.adc.read_voltage(channel)
        # presumably we are not supposed to use the getADCVoltage correction here?
        return abs((raw_voltage - self.midOffset) * 1000 / self.milliVoltPerAmp)


    # TODO: I haven't pulled this one apart so much because I'm not sure what its doing
    def getThermistor(self, channel):
        raw_voltage = self.adc.read_voltage(channel)
        if raw_voltage == 0:
            return 0
        rTherm = (self.rVoltDiv * (5-raw_voltage)) / raw_voltage
        retTemp = (self.beta / (math.log(rTherm / self.rInf))) - kelvinToCentigrade
        if not (self.MIN_TEMP < retTemp < self.MAX_TEMP):
            retTemp = -1 # input must be floating - we can't be near outside this range!! Return error value
            # TODO: Isn't -1 degrees possible if the unit is in a cold place? We need clear error data to propagate to the server
        return round(retTemp, 1)

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
        PM2_5, PM10 = self.getParticulates()
        return {
            "dt": datetime.utcnow(),
            "data": {
                "battery_voltage": self.getADCVoltage(1),
                "cooker_current": self.getADCCurrent(2),
                "pv_current": self.getADCCurrent(3),
                "pv_voltage": self.getADCVoltage(4),
                "ch5_raw": self.adc.read_voltage(5),
                "usb_load_current": self.getADCCurrent(6),
                "pi_current": self.getADCCurrent(7),
                "temperature": self.getThermistor(8),
                # "temperature": self.getLM35(8),
                "PM2.5": PM2_5,
                "PM10": PM10
            }
        }
