

import serial
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import time
from pymodbus import Framer
import numpy as np
import ctypes

def convert_16bits_integer(np_binary_array):
    low_8bits = np.packbits(np_binary_array[:8]);
    high_8bits = np.packbits(np_binary_array[8:]);
    print(low_8bits)
    print(high_8bits);
    return high_8bits << 8 | low_8bits;


class fengkong_current_detector(object):
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=19200, parity='N',
                 data_bits=8, stop_bits=1, timeout=0.01, unit=0x01):
        self.serial_port = serial_port  # Replace this with your serial port
        self.baud_rate = baud_rate
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.timeout = timeout;
        self.unit = unit;
        self.serial = serial.Serial("/dev/ttyUSB0", baud_rate)
        self.baud_rate_dict = {3:1200,4:2400,5:4800,6:9600,7:19200}
        self.client = ModbusSerialClient(
            method='rtu',
            Framer=Framer.RTU,
            port=self.serial_port,
            baudrate=self.baud_rate,
            parity=self.parity,
            bytesize=self.data_bits,
            stopbits=self.stop_bits,
            timeout=self.timeout,
            errorcheck="crc"
        )

        try:
            connection = self.client.connect();
            if connection:
                print("Connected to Modbus RTU device " + "fengkong_current_detector");
            else:
                print("Failure to do connection ")
        except Exception as e:
            print(e);

    def set_controller_address(self, unit=-1, baud_rate=-1):
        '''
        set slave id and baud_rate for IO_relay
        :param unit: uint8, slave id
        :param baud_rate: integer from 3 to 7, baurd rate choice
        :return: bool, True for success vice versa
        '''

        if 3 <= baud_rate <= 7 and self.baud_rate != self.baud_rate_dict[baud_rate]:
            result = self.client.write_registers(address=0x20, values=baud_rate, slave=self.unit);
            if isinstance(result, ModbusException):
                print("Failure to set baudrate",result)
                return False;

        if 0 < unit < 0xFF and self.unit != unit:
            result = self.client.write_registers(address=0x57, values=unit, slave=self.unit);
        print("Success to set slave id and baudrate: restarting!!!");
        self.unit = unit;
        self.baud_rate = self.baud_rate_dict[baud_rate];
        self.client.close();
        self.client = ModbusSerialClient(
            method='rtu',
            Framer=Framer.RTU,
            port=self.serial_port,
            baudrate=self.baud_rate,
            parity=self.parity,
            bytesize=self.data_bits,
            stopbits=self.stop_bits,
            timeout=self.timeout,
            errorcheck="crc"
        );
        try:
            connection = self.client.connect();
            if connection:
                print("Connected to Modbus RTU device");
            else:
                print("Failure to do connection ")
        except Exception as e:
            print(e);
        print("Done")
        return True;
    def read_current(self):
        '''
        Reads the current
        :return:
        '''
        result = self.client.read_holding_registers(address=0x0056, count=1, slave=self.unit);
        if isinstance(result, ModbusException):
            print("Fail to read current",result)
            return None;
        return result.registers[0]*(20-0)/10000-0;

    def close(self):
        self.serial.close();
        self.client.close();

    def connect(self):
        self.client.connect();

    def write_bytes(self, hex_bytes):
        """
        Write a bytes to the modbus server.
        self.write_bytes("02 06 00 02 00 01 E9 F9")
        Args:
            hex_bytes:

        Returns:

        """
        byte = bytes.fromhex(hex_bytes)
        self.serial.write(byte)
