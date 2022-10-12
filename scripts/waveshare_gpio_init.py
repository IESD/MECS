import pigpio
import time

OUR_PIN = 17
pi = pigpio.pi()

time.sleep(1)
pi.set_mode(OUR_PIN, pigpio.OUTPUT)

time.sleep(1)
pi.write(OUR_PIN, 0)

time.sleep(1)
pi.write(OUR_PIN, 1)
