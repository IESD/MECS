"""
For managing a MUST EP 3000 Pro AC Inverter device to read via serial (RS232 via USB)
Most of the code is error handling
The key things are to create the sensors and calculate the readings correctly

TODO!!! Check the drivers on Pi Zero W - might need https://github.com/juliagoda/CH341SER
"""

import logging

from ... import MECSConfigError, MECSHardwareError
from serial import Serial, SerialError

log = logging.getLogger(__name__)

class EP3000Error(MECSConfigError): pass

class EP3000Device:
    def __init__(self, hardware_required=True, **kwargs):
        """
        Ingest configuration data
        Raise MECSConfigError if anything is wrong
        """
        try:
            portname = kwargs.get('serial_port','/dev/ttyUSB0')
            baud_rate = kwargs.get('baud_rate', 2400)
            sensors = kwargs['sensors']
        except KeyError as e:
            raise Error(f"Missing parameter: {e}")

        self.commands = {'main_readings':b"Q1\r",
                         'load_frequency':b"F\r",
                         'error_query':b"G?\r",
                         'charge_current':b"X\r"}

        try:
            self.serial_port = Serial(portname, baud_rate)
        except ValueError as e:
            log.info("Parameter out of range - is your baud rate right?")
            pass
        except SerialError as e:
            log.warn("Can't open EP3000 on specified serial port - is it right?")
            if (hardware_required):
                raise(MECSHardwareError('No EP3000 on serial interface'))

        self.read_vars = {}

        log.debug(f"{self} created")

    def getCommand(self, command):
        '''
        Sends a command string via the serial port
        NB This function is deliberately highly fault tolerant, returning None rather than propogating Exceptions
        This is due serial comms having potential for upstream errors e.g. in Serial to USB converter

        returns: string response or None if empty or on error
        '''
        if not self.serial_port.is_open:
            try:
                self.serial_port.open()
            except SerialException:
                log.warn('Serial port cannot be opened right now')
                return None

        try:
            self.serial_port.write(command)
            self.serial_port.flush()
        except SerialException:
            log.warning('Cannot write to serial port, is it correctly configured?')
            return None

        if (self.serial_port.in_waiting > 0):
            return_data = self.serial_port.read_all()
            return return_data
        else:
            return None

    def parse_data(self):
        main_readings = self.getCommand(self.commands['main_readings'])
        if main_readings:
            input_volt = self.try_parse(main_readings[1:6])
            input_fault_v = self.try_parse(main_readings[7:12])
            output_volt = self.try_parse(main_readings[13:18])
            output_curr = self.try_parse(main_readings[19:22])
            input_f_ = self.try_parse(main_readings[23:27])
            batt_volt = self.try_parse(main_readings[28:32])
            inverter_temp_raw = main_readings[33:37]
            temp_bias = int(try_parse(inverter_temp_raw[0]))
            inverter_temp = str(((temp_bias-48)*10)+float(try_parse(inverter_temp_raw[1:])))
        else:
            log.warning('No data returned in response to main_reading command')
            return {'Input voltage': None,
             'Output voltage': None,
             'Output_current': None,
             'Battery voltage': None,
             'Inverter temp': None,
             'Charge current': None}

        charge_current_raw = self.getCommand(self.commands['charge_current'])
        if charge_current_raw:
            current_hex = try_parse(charge_current_raw.split(b' ')[0])
            charge_current = str(int(current_hex,16))
        else:
            log.warning('Charge current not returned')
            charge_current = None

        return {'Input voltage':input_volt,
                'Output voltage':output_volt,
                'Output_current':output_curr,
                'Battery voltage':batt_volt,
                'Inverter temp':inverter_temp,
                'Charge current':charge_current }

    def try_parse(self, in_bytes):
        try:
            return in_bytes.decode('utf-8')
        except:
            log.debug('Failed to parse input bytes into string')
            return None

    def read(self):
        all_vals = self.parse_data()
        for k in self.return_keys:
            yield k, all_vals[k]

    def readings(self):
        return dict(self.read())

    def __repr__(self):
        read_vars = ", ".join(['Input voltage','Output voltage','Output_current','Battery voltage','Inverter temp','Charge current'])
        return f"EP3000 Device, configured to read ({read_vars})"
