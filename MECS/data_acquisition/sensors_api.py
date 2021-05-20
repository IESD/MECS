#!/usr/bin/python3

import ADCPi
import time
import os
#import serial
import math
from aqi import *
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


def calcCurrent(inval):
    return ((inval) - 2.624202) / 0.11761066 # Calibration constants by experiment

def calcVoltage(inVal):
   return inVal*(30+5.185)/5.185 # Figures from calculation of sensor potential divider and ADC Pi input divider


def calcAcCurrent(inVal):
    return 20/2.6*(inVal - 0.056) #Spec says 20A/V, zero calibration by observation - need better way


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

def getTempFromVolts(voltage):
    print ("voltage4Temp %02f" % voltage)
    kelvinToCentigrade = 273
    retTemp = 0
    T0 = 25 + kelvinToCentigrade # Kelvin
    R0 = 103 # 1000 1kOhm at 25 deg C
    beta = 3950  #3260
    #rTherm = 240 * (0.5 + (voltage/5)) / (0.5 - (voltage/5)) #Calibrate here!!!! 
    rTherm = (220 * voltage) /  (5 -  voltage)
    print ("rTherm %02f" % rTherm)
    rInf = R0 * math.exp(-beta / T0)
    print ("rInf %02f" % rInf)
    retTemp = beta / (math.log(rTherm / rInf))
    retTemp -= kelvinToCentigrade
    if retTemp < 5 or retTemp > 100:
        retTemp = 0 # input must be floating - we can't be near freezing!! 
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

# Need this in __init__() if and when you make this a module/class

#port = serial.Serial("/dev/serial0", baudrate=9600, timeout=3.0)

# These are possible serial messages to send to the CO2 sensor as per
# https://github.com/Arduinolibrary/DFRobot_Gravity_UART_Infrared_CO2_Sensor/raw/master/MH-Z16%20CO2%20Datasheet.pdf

#uart_read_hex = [0xFF,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79]
#uart_calibrate_zero_hex = [0xFF,0x01,0x87,0x00,0x00,0x00,0x00,0x00,0x78] 
#uart_calibrate_span_hex = [0xFF,0x01,0x88,0x07,0xD0,0x00,0x00,0x00,0xA0]



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
            "Particular_PM2.5" : partValues[0],
            "Particular_PM10": partValues[1]
        }
    }




while (True):

    # clear the console
    os.system('clear')
    partValues = getParticulars()
    # read from adc channels and print to screen
    #print ("Raw on channel 3: %02f" % adc.read_voltage(3))
    print ("Voltage on battery (ch1): %02f" % calcVoltage(adc.read_voltage(1)))
    print ("Current on cooker (ch2): %02f" % calcCurrent(adc.read_voltage(2)))
    print ("Current on PV (ch3): %02f" % calcCurrent(adc.read_voltage(3)))
    print ("Voltage on PV?? (ch4): %02f" % calcVoltage(adc.read_voltage(4))) #Check - The  device needs to be moved
    print ("Temp (ch5) %02f" % getTempFromVolts(adc.read_voltage(5)))
    print ("Current on USB load (ch6): %02f" % calcCurrent(adc.read_voltage(6)))
    print ("Current on Pi (ch7): %02f" % calcCurrent(adc.read_voltage(7)))
    print ("Particular_PM2.5: %02f" % partValues[0])
    print ("Particular_PM10: %02f" % partValues[1])
    #print ("RMS no conversion channel 4: %02f" % sampleAC(adc,4))
    #print ("RMS AC Volts on channel 4: %02f" % calcACvolts(adc,4))
    #print ("AC Current on channel 7: %02f" % calcAcCurrent(adc.read_voltage(7))) #20 is because clamp is 20A/V


   # wait 0.5 seconds before reading the pins again
    time.sleep(5)
