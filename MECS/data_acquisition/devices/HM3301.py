import pigpio
from time import sleep
import logging
from ... import MECSConfigError, MECSHardwareError

log = logging.getLogger(__name__)


class HM3301Device(object):
    DATA_CNT = 29
    default_SDA_pin = 20
    default_SCL_pin = 21
    default_baud = 20000
    default_i2c_address = 0x40

    fully_initialised = False

    offsets = {
        'PM1.0': 4,  # PM1.0 Standard particulate matter concentration Unit:ug/m3
        'PM2.5': 6,  # PM2.5 Standard particulate matter concentration Unit:ug/m3
        'PM10': 8,  # PM10  Standard particulate matter concentration Unit:ug/m3
        'PM_1.0_conctrt_atmosph': 10,  # PM1.0 Atmospheric environment concentration ,unit:ug/m3
        'PM_2.5_conctrt_atmosph': 12,  # PM2.5 Atmospheric environment concentration ,unit:ug/m3
        'PM_10_conctrt_atmosph': 14,  # PM10  Atmospheric environment concentration ,unit:ug/m3
        'Count 0.3um+ in 1l air': 16,  # The number of particles with diameter 0.3um or above in 1 liter of air
        'Count 0.5um+ in 1l air': 18,  # The number of particles with diameter 0.5um or above in 1 liter of air
        'Count 1.0um+ in 1l air': 20,  # The number of particles with diameter 1.0um or above in 1 liter of air
        'Count 2.5um+ in 1l air': 22,  # The number of particles with diameter 2.5um or above in 1 liter of air
        'Count 5.0um+ in 1l air': 24,  # The number of particles with diameter 5.0um or above in 1 liter of air
        'Count 10.0um+ in 1l air': 26  # The number of particles with diameter 10.0um or above in 1 liter of air
    }

    return_keys = ['PM2.5','PM10']

    def __init__(self, hardware_required, **kwargs):
        print("Initialising the HM3301")
        self.pi = pigpio.pi()
        try:
            self.SDA = kwargs['SDA']
        except KeyError:
            log.warning(f'No SDA pin specified, using default {HM3301Device.default_SDA_pin}')
            self.SDA = HM3301Device.default_SDA_pin

        try:
            self.SCL = kwargs['SCL']
        except KeyError:
            log.warning(f'No SCL pin specified, using default {HM3301Device.default_SCL_pin}')
            self.SCL = HM3301Device.default_SCL_pin

        try:
            self.i2c_address = kwargs['i2c_address']
        except KeyError:
            log.warning(f'No SDA pin specified, using default {HM3301Device.default_i2c_address}')
            self.i2c_address = HM3301Device.default_i2c_address

        try:
            self.label = kwargs['label']
        except KeyError:
            log.warning('No label specified, using default HM3301_Sensor')
            self.label = 'HM3301_Sensor'

        # Set up an empty dictionary to hold the latest readings
        self.latest_data = {}

        # set pullups - not necessary with Pi2Grover
        log.info("Set the comms lines to pull up")
        self.pi.set_pull_up_down(self.SDA, pigpio.PUD_UP)
        self.pi.set_pull_up_down(self.SCL, pigpio.PUD_UP)

        # pigpio spits ungraceful error if channel left open on SDA, so
        # as precaution handle errors here as they may be common
        log.debug("Initialising the comms line - deal with exceptions here")
        pigpio.exceptions = False
        retries = 3
        try_count = 0
        h = -1
        while try_count < retries and h < 0:
            h = self.pi.bb_i2c_open(self.SDA, self.SCL, self.default_baud)
            if h == pigpio.PI_GPIO_IN_USE:
                self.pi.bb_i2c_close(self.SDA)
            try_count += 1
        if h < 0:
            log.error('Pigpio cannot open i2c for particulate sensor')
            if hardware_required:
                raise MECSHardwareError("Couldn't access INA3221 device")
            return

        pigpio.exceptions = True

        (count, data) = self.pi.bb_i2c_zip(
            self.SDA, [4, self.i2c_address, 2, 7, 1, 0x80, 2, 7, 1, 0x88, 3, 0])
        sleep(10.0 / 1000.0)

        self.fully_initialised = True
        log.info(f"HM3301 {self.label} fully initialised")

    def read_HM3301_data(self):
        (count, data) = self.pi.bb_i2c_zip(
            self.SDA, [4, self.i2c_address, 2, 7, 1, 0x81, 3, 2, 6, self.DATA_CNT, 3, 0])
        return list(data)

    def close(self):
        self.pi.bb_i2c_close(self.SDA)
        self.pi.stop()

    def checksum(self, data):
        chksum = 0
        for i in range(self.DATA_CNT - 1):
            chksum += data[i]
        chksum = chksum & 0xff
        return chksum == data[28]

    def parse_data(self, data):
        if not self.checksum(data):
            return {}

        for key, val in self.offsets.items():
            self.latest_data[key] = data[val] << 8 | data[val + 1]
        return self.latest_data

    def read(self):
        data = self.read_HM3301_data()
        all_vals = self.parse_data(data)
        for k in self.return_keys:
            yield k, all_vals[k]

    def __repr__(self):
        return f"HM3301Device({self.label!r}, i2c on pins {self.SDA!r} and {self.SCL!r}, address {self.i2c_address!r})"
