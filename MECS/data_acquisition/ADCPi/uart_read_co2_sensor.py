import serial
import time

# Code to reed the Gravity Co2 sensor from dfrobot (a.k.a. Grove sensor at seeedstudios I think)
# Infrared gas sensing - details at https://wiki.dfrobot.com/Infrared_CO2_Sensor_0-50000ppm_SKU__SEN0220#More
# Based on spec found at https://github.com/Arduinolibrary/DFRobot_Gravity_UART_Infrared_CO2_Sensor/raw/master/MH-Z16%20CO2%20Datasheet.pdf
port = serial.Serial("/dev/serial0", baudrate=9600, timeout=3.0)

# These are possible serial messages to send to the CO2 sensor as per linked spec sheet
uart_read_hex = [0xFF,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79]
#uart_calibrate_zero_hex = [0xFF,0x01,0x87,0x00,0x00,0x00,0x00,0x00,0x78]
#uart_calibrate_span_hex = [0xFF,0x01,0x88,0x07,0xD0,0x00,0x00,0x00,0xA0]

def read_co2_sensor():
    co2 = -1 # Error value, returned if a problem
    port.write(serial.to_bytes(uart_read_hex))
    while (not(port.in_waiting)):
        time.sleep(0.1) #Added sleep to allow time to read
    for x in range(9):
        ch=port.read()
        if x ==2:
            hi=int.from_bytes(ch,byteorder='little')
        if x == 3:
            low= int.from_bytes(ch,byteorder='little')
        if x == 8:
            co2 = hi*256+low
    return co2

if __name__=='__main__':
    while True:
        co2_conc = read_co2_sensor()
        print('CO_2 concentration is : {conc} ppm \n'.format(conc=co2_conc))
