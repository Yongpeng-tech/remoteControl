# This is a sample Python script.
import binascii

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadBuilder , BinaryPayloadDecoder
import time
from pymodbus.constants import Endian
import serial
from remote_control_alarm import Alarm

class ConnectError(Exception):
    def __init__(self, message="Connect Failure"):
        self.message = message
        super().__init__(self.message)

class ModbusController(object):
    def __init__(self, serial_port="/dev/ttyUSB0", baud_rate=9600, parity='N',
                 data_bits=8, stop_bits=1, timeout=0.001):
        self.serial_port = serial_port  # Replace this with your serial port
        self.baud_rate = baud_rate
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.timeout = timeout;

        self.serial = serial.Serial("/dev/ttyUSB0", baud_rate)
        self.client = ModbusSerialClient(
            method="RTU",
            port=self.serial_port,
            baudrate=self.baud_rate,
            parity=self.parity,
            bytesize=self.data_bits,
            stopbits=self.stop_bits,
            timeout=self.timeout,
            errorcheck="crc"
        )

    def connect(self):
        try:
            self.client.connect();
            print("successfully connected" + self.serial_port);
        except Exception as e:
            print("failure to connect ,e")

    def read_register(self,starting_address = 0,
                       quantity = 1,unit = 1):
        try:
            result = self.client.read_holding_registers(starting_address,quantity,unit)
            # Check if the read operation was successful
            if not result.isError():
                # Extract and print the values read from the registers
                decoder = BinaryPayloadDecoder.fromRegisters(
                    result.registers,
                    byteorder=Endian.Big, wordorder=Endian.Big
                )
                print("Values read from registers:", result.registers)
        except Exception as e:
            print(f"Failed to read registers. Error: {result}",e)
            raise ModbusIOException("read register error");
    def write_register(self,starting_address = 0,
                       twobytedata = 0,unit = 1):

        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_16bit_uint(twobytedata)  # Example data, modify as needed
        payload = builder.to_registers()

        #print(payload)
        # Send the constructed Modbus RTU message
        try:
            result = self.client.write_register(address=starting_address,
                                                value=twobytedata, unit=unit)
        # Check if the read operation was successful
            if not result.isError():
                # Extract and print the values read from the registers
                print("Write Operation is successful");
        except Exception as e:
            print("Failed to read registers. Error: ",e)

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


class Standard_modbus_alarm(ModbusController):
    def __init__(self, ModbusSever,unit = 0x01):
        super().__init__(ModbusSever.serial_port, ModbusSever.baud_rate
                 ,ModbusSever.parity,ModbusSever.data_bits,ModbusSever.stop_bits,ModbusSever.timeout)  # Calling the Parent class's __init__ method
        self.unit = unit;
    def alarmVolumeSet(self,volume = 15):
        try:
            self.write_register(starting_address=0x04,twobytedata=volume,unit = self.unit);
            #self.read_register(starting_address=0x01,quantity=1,unit = self.unit)
            print('volume set as ' + str(volume));
        except ModbusIOException as e:
            print("Wrong to set the alarm volume",e);

    def alarmPlayMode(self,mode = 1):
        try:
            self.write_register(starting_address=9, twobytedata=mode, unit=self.unit);
        except ModbusIOException as e:
            print("Wrong to set the alarm play mode",e)

    def setAlarmAddress(self,unit):
        try:
            self.write_register(starting_address=0x0B, twobytedata=unit, unit=self.unit);
            self.unit = unit;
        except:
            print("Wrong to assign uint ID to alarm device");

    def playAlarm(self):
        try:
            request = self.write_register(starting_address= 1, twobytedata= 1, unit=self.unit);
            print('start to play alarm');
            self.write_bytes('EF AA 01 AA 02 00 AC EF 55');
        except Exception \
                as e:
            print("Failure to let alarm play",e);

    def stopAlarm(self):
        try:
            self.write_register(starting_address=2, twobytedata= 1, unit=self.unit);
            self.write_bytes('EF AA 01 AA 02 00 AC EF 55');
            print('stop playing alarm');
        except Exception as e:
            print("Failure to let alarm stop",e);

    def check_configuration(self):
        # check the configuration
        modbusClient.serial.reset_input_buffer();
        modbusClient.write_bytes('EF FF FF A6 33 EF 55');
        result = modbusClient.serial.read(10);
        print(['{:02x}'.format(b) for b in result])
        # self.client.close();
        # time.sleep(1);
        # self.client.connect();
    def reset_alarm(self):
        # reset the alarm as default setting
        modbusClient.serial.reset_input_buffer();
        modbusClient.write_bytes('EF FF FF A7 33 EF 55');
        result = modbusClient.serial.read(7);
        print(['{:02x}'.format(b) for b in result])
        self.client.close();
        time.sleep(1);
        self.client.connect();



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    alarm = Alarm(serial_port="/dev/ttyUSB0", baud_rate= 9600,unit = 0x01);
    alarm.setAlarmVolume(volume=5)
    alarm.playAlarm();
    time.sleep(1);
    alarm.stopAlarm();
    exit(0);



# See PyCharm help at https://www.jetbrains.com/help/pycharm/