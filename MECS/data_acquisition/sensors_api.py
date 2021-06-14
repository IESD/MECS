#!/usr/bin/python3

"""
================================================
Coded modified from the ABElectronics ADC Pi

Requires python 3 smbus to be installed
================================================

Initialise the ADC device using the default addresses and sample rate,
change this value if you have changed the address selection jumpers

Sample rate can be 12,14, 16 or 18
"""

import time
import os
import math
from datetime import datetime

from .sds011.SDS011 import SDS011, serial
from .ADCPi import ADCPi, ABEHelpers

#Initialise the SDS011 air particulate density sensor.
try:
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
except serial.serialutil.SerialException as exc:
    print(exc)
    sensor = False

i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x68, 0x69, 12)

INPUT_IMPEDANCE = 16800 #Input impedance of the ADC - needed when calculating using external voltage dividers
MIN_TEMP = 5
MAX_TEMP = 150

R_TOP = 30000
R_BOTTOM = 7500
R_EFFECTIVE = R_BOTTOM * INPUT_IMPEDANCE / (R_BOTTOM + INPUT_IMPEDANCE)



#######
# calculate Current from voltage signal from this ACS712 board.
# Note we are concerned with magnitude, rather than direction, hence using abs
#######
def calcCurrent(inval):
    midOffset = 2.5 # 2.624202 # From experiment calibration - nominally Vcc/2, should be 2.5
    milliVoltPerAmp = 100 # 117.61066 #From experiment calibration - nominally 100 on the +/-20A version
    return abs((inval - midOffset) * 1000 / milliVoltPerAmp) # Calibration constants by experiment

#####
# Calculates voltage on input of voltage sensor module described here
# https://www.electronicshub.org/interfacing-voltage-sensor-with-arduino/#:~:text=The%20Voltage%20Sensor%20is%20a%20simple%20module%20that,in%20this%20project.%20Pins%20of%20the%20Voltage%20Sensor
# Note that that 7.5k resistor of that module is in parallel with the input impedance of the ADC Pi
# so that must be incorporated
#####
def calcVoltage(inVal):
   return inVal * (R_TOP + R_EFFECTIVE) / R_EFFECTIVE

######
# Work in progress to use AC current clamp - TODO - needs improvement
######
def calcAcCurrent(inVal):
    return 20 / 2.6 * (inVal-0.056) #Spec says 20A/V, zero calibration by observation - need better way

#########
# This is needed if measuring an AC voltage directly on the ADC Pi channel
# It is error prone as it relies on sampling the waveform and finding rms value, so
# smoothing in analogue componentry external is preferred.
#########

def sampleRMS(adc, channel, n=1000):
    """
    A more pythonic version of the below function
    Though if we want speed then we should consider using numpy for this
    """
    adc.set_conversion_mode(1)
    readings = [adc.read_voltage(channel) for i in range(n)]
    adc.set_conversion_mode(0)
    mean_reading = sum(readings) / len(readings)
    squared = [(r-mean_reading)**2 for r in readings]
    mean_squared = sum(squared) / len(squared)
    return math.sqrt(mean_squared)

def sampleAC(adc, channel):
    adc.set_conversion_mode(1)
    readings = []
    for i in range(1000):
        readings.append(adc.read_voltage(channel))
    sum = 0
    for r in readings:
        sum = sum + r
    mid_ref_v = sum / len(readings)
    sum = 0
    for r in readings:
        sum = sum + (r-mid_ref_v)**2
    sq_avg = sum / len(readings)
    rms = math.sqrt(sq_avg)
    adc.set_conversion_mode(0)
    return rms

def calcACvolts(adc, channel):
    rms = sampleAC(adc,channel)
    AC_conv_factor = 181.4
    return AC_conv_factor * rms

#####
# This function assumes that the external setup is a thermistor between VCC and ADC input, with
# rBias between the ADC input and ground, forming a voltage divider.  From this, rTherm can be calculated
# from voltage
########
def getTempFromVolts(voltage):
    #print ("voltage4Temp %02f" % voltage)
    if voltage == 0:
        return 0
    kelvinToCentigrade = 273
    retTemp = 0
    rBias = 9970 # calibrate carefully here
    T0 = 25 + kelvinToCentigrade # 25 deg C in Kelvin
    R0 = 10000 # 10000 1kOhm at 25 deg C - part of thermistor spec
    beta = 3950 # part of thermistor spec
    rVoltDiv = (rBias * INPUT_IMPEDANCE) / (rBias+INPUT_IMPEDANCE)
    rTherm = (rVoltDiv * (5-voltage)) / voltage
    #rTherm = (220 * voltage) /  (5 -  voltage)
    #print ("rTherm %02f" % rTherm)
    rInf = R0 * math.exp(-beta / T0)
    #print ("rInf %02f" % rInf)
    retTemp = beta / (math.log(rTherm / rInf))
    retTemp -= kelvinToCentigrade
    if retTemp < MIN_TEMP or retTemp > MAX_TEMP:
        retTemp = -1 # input must be floating - we can't be near outside this range!! Return error value
    return round(retTemp, 1)



####
# Code snippet added by Henrik 2021-05-28
# Code snippet modified by Henrik 2021-06-02
# This function converts LM35 voltage readings  to temprature
# Output voltage signal is given by 10mV/C*T
####
def getTempFromLM35(mVolts):
   lm35_scale_factor = 10 # Linear scale factor 10mV/C
   conv_to_volts = 1000   # Convert to volts 1000mV per 1 Volts
   temp = (mVolts/lm35_scale_factor) * conv_to_volts

   # Add debugging/logging code here

   return round(temp,3)

#The current code for air quality oly works with python2. Under python3 the construct_command function needs to convert the UTF string to bytes.
#The following module works with python3. Command: git clone https://github.com/ikalchev/py-sds011.git
# cd py-sds011/
# pip3 install -e .
#
def getParticulars():
    if not sensor:
        return (0, 0)

    for t in range(10):
        values = sensor.query()
        if values is not None and len(values) == 2:
            return values
        sensor.sleep()
        sensor.sleep(sleep=False)
        time.sleep(5)

    return (0, 0)

def raw_readings():
    """A function to represent gathering data from all the sensors"""
    partValues = getParticulars()
    return {
        "dt": datetime.utcnow(),
        "data": {
            "Battery_Voltage_ch1": calcVoltage(adc.read_voltage(1)),
            "Cooker_Current_ch2": calcCurrent(adc.read_voltage(2)),
            "PV_Current_ch3": calcCurrent(adc.read_voltage(3)),
            "PV_Voltage??_ch4": calcVoltage(adc.read_voltage(4)),
            "USB_LOAD_Current_ch6": calcCurrent(adc.read_voltage(6)),
            "Pi_Current_ch7": calcCurrent(adc.read_voltage(7)),
            "Temp_ch8": getTempFromVolts(adc.read_voltage(8)),
            #"Raw read_ch8": adc.read_voltage(8),
            #"Temp_ch8": getTempFromLM35(adc.read_voltage(8)),
            "Particular_PM2.5" : partValues[0],
            "Particular_PM10": partValues[1]
        }
    }
