#!/usr/bin/python3

import time
import os
#import serial
import math
from datetime import datetime

from . import ADCPi
#from aqi import *
"""
================================================
Coded modified from the ABElectronics ADC Pi

Requires python 3 smbus to be installed
================================================

Initialise the ADC device using the default addresses and sample rate,
change this value if you have changed the address selection jumpers

Sample rate can be 12,14, 16 or 18
"""

i2c_helper = ADCPi.ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi.ADCPi(bus, 0x68, 0x69, 12)

# change the 2.5 value to be half of the supply voltage.
_adcpi_input_impedance = 16800 #Input impedance of the ADC - needed when calculating using external voltage dividers
_min_temp = 5
_max_temp = 150

#######
# calculate Current from voltage signal from this ACS712 board.
# Note we are concerned with magnitude, rather than direction, hence using abs
#######
def calcCurrent(inval):
    #print('Raw voltage in %02f'%inval)
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
   rTop = 30000
   rBottom = 7500
   rEffective = rBottom*_adcpi_input_impedance / (rBottom+_adcpi_input_impedance)
   return inVal*(rTop+rEffective)/rEffective

######
# Work in progress to use AC current clamp - TODO - needs improvement
######
def calcAcCurrent(inVal):
    return 20/2.6*(inVal - 0.056) #Spec says 20A/V, zero calibration by observation - need better way

#########
# This is needed if measuring an AC voltage directly on the ADC Pi channel
# It is error prone as it relies on sampling the waveform and finding rms value, so
# smoothing in analogue componentry external is preferred.
#########
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
    rVoltDiv = (rBias * _adcpi_input_impedance) / (rBias+_adcpi_input_impedance)
    rTherm = (rVoltDiv*(5-voltage))/voltage
    #rTherm = (220 * voltage) /  (5 -  voltage)
    #print ("rTherm %02f" % rTherm)
    rInf = R0 * math.exp(-beta / T0)
    #print ("rInf %02f" % rInf)
    retTemp = beta / (math.log(rTherm / rInf))
    retTemp -= kelvinToCentigrade
    if retTemp < _min_temp or retTemp > _max_temp:
        retTemp = -1 # input must be floating - we can't be near outside this range!! Return error value
    return round(retTemp,1)


#The current code for air quality oly works with python2. Under python3 the construct_command function needs to convert the UTF string to bytes.
def getParticulars():
    '''cmd_set_sleep(0)
    cmd_firmware_ver()
    cmd_set_working_period(PERIOD_CONTINUOUS)
    cmd_set_mode(MODE_QUERY);
    for t in range(15):
        values = cmd_query_data();
        if values is not None and len(values) == 2:
            return values'''
    return [0,0]

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
            "Particular_PM2.5" : partValues[0],
            "Particular_PM10": partValues[1]
        }
    }


if __name__=='__main__':
    while (True):
        # clear the console
        os.system('clear')
        print(raw_readings())

        # wait 2 seconds before reading the pins again
        time.sleep(2)
