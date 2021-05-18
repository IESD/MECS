import serial
import time

port = serial.Serial("/dev/serial0", baudrate=9600, timeout=3.0)

hexdata = [0xFF,0x01,0x86,0x00,0x00,0x00,0x00,0x00,0x79]


while True:
    print(serial.to_bytes(hexdata))
    port.write(serial.to_bytes(hexdata))
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
            print('CO_2 concentration is : {conc} ppm \n'.format(conc=co2))
