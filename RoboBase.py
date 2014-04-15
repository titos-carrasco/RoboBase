# -*- coding: utf-8 -*-
"""Bluetooth control for a generic Arduino based robot

"""

import serial
import threading
import time

class RoboBase:
    """Class to control the robot

    Usage:
        robot = DaguCar("/dev/rfcomm0")
        if(robot.IsConnected()):
            robot.SetMotors(-255, 255)
            time.sleep(1)
            robot.SetMotors(0, 0)
            robot.Close()
    """

    PACKET_LENGTH = 8;

    def __init__(self, port, bauds=9600):
        """Create the robot object and open a connection to it.

        Args:
            port: The serial port to use (string)
            bauds: The speed for the serial communication (integer)

        Raises:
            KeyboardInterrupt
        """

        self._lock = threading.Lock()
        self._ser = None
        for t in range(4):
            try:
                self._ser = serial.Serial(port, baudrate=bauds, bytesize=8,
                                           parity='N', stopbits=1, timeout=1)
                self._Debug('RoboBase.Init: Connected to %s,  %d bps' %
                            (port, bauds))
                self._Debug('RoboBase.Init: Ignoring old data')
                self._ConsumeOldData()
                break
            except serial.SerialException:
                self._Debug('RoboBase.Init: SerialException')
            except ValueError:
                self._Debug('RoboBase.Init: ValueError')
            except IOError:
                self._Debug('RoboBase.Init: IOError')
            except KeyboardInterrupt:
                self._Debug('RoboBase.Init: KeyboardInterrupt')
                raise

    def _Lock(self):
        """Get an exclusive access to the robot."""
        self._lock.acquire()
        if(self._ser!=None and self._ser.isOpen()):
            return True
        else:
            self._lock.release()
            return False

    def _Unlock(self):
        """Release the exclusive access to the robot."""
        try:
            self._lock.release()
        except:
            pass

    def _Debug(self, val):
        """Simple console debug."""
        print val

    def _ConsumeOldData(self):
        """Consume data from latest requests"""
        timeout = self._ser.timeout
        self._ser.timeout = 1
        while(True):
            try:
                self._ser.read(1000)
            finally:
                break
        self._ser.timeout = timeout

    def IsConnected(self):
        """True if connected to the robot."""
        try:
            if(self._ser.isOpen()):
                return True
        except:
            pass
        return False

    def Close(self):
        """Close the connection to the robot."""
        if(self._Lock()):
            self._ser.close()
            self._ser = None
            self._Unlock()

    # Commands for the robot
    CMD_SET_MOTORS = 0x01
    CMD_PING = 0x02
    CMD_BEEP = 0x03
    CMD_INFO = 0x04

    def _SendCommand(self, packet):
        """Send a command to the robot.

         Args:
            packet: PACKET_LENGTH byte packets.
                    The first byte is the command (CMD_XX)
        """
        self._ser.write(packet)
        self._ser.flush()
        r = self._ser.read(self.PACKET_LENGTH)  # robot must return the packet
        r = bytearray(r)
        if(packet !=r ):
            self._Debug('Packet Mismatch')
            self._Debug(list(packet))
            self._Debug(list(r))

    def SetMotors(self, motor1, motor2):
        """Applies power to the motors

        Args:
            motor1, motor2 : power for the motor (-255 - 255)
                             0 = stop, <0 backward, >0 forward
        """
        if(self._Lock()):
            try:
                motor1, motor2 = int(motor1), int(motor2)
                if(motor1<0):
                    m1_dir = 0x00;
                else:
                    m1_dir = 0x01
                if(motor2<0):
                    m2_dir = 0x00
                else:
                    m2_dir = 0x01
                packet = bytearray(self.PACKET_LENGTH)
                packet[0] = 0x01
                packet[1] = m1_dir
                packet[2] = abs(motor1) & 0xFF
                packet[3] = m2_dir
                packet[4] = abs(motor2) & 0XFF
                self._SendCommand(packet)
            except serial.SerialTimeoutException:
                self._Debug('RoboBase.SetMotors: SerialTimeoutException')
            except serial.SerialException:
                self._Debug('RoboBase.SetMotors: SerialException')
            except:
                self._Debug('RoboBase.SetMotors: Unexpected Exception')
            self._Unlock()

    def Ping(self, max_distance):
        """Gets the distance reported by the ping sensor

        Args:
            max_distance: max distance for detection (integer)

        Returns:
            the distance to an obstacle
        """
        r = 0
        if(self._Lock()):
            try:
                max_distance = abs(int(max_distance)) & 0xFFFF
                packet = bytearray(self.PACKET_LENGTH)
                packet[0] = 0x02
                packet[1] = (max_distance >> 8)
                packet[2] = (max_distance & 0xFF)
                self._SendCommand(packet)
                r = self._Read2UBytes()/100.0
            except serial.SerialTimeoutException:
                self._Debug('RoboBase.Ping: SerialTimeoutException')
            except serial.SerialException:
                self._Debug('RoboBase.Ping: SerialException')
            except:
                self._Debug('RoboBase.Ping: Unexpected Exception')
            self._Unlock()
        return r

    def Beep(self, freq, duration):
        """Make a sound

        Args:
            freq: frequency (integer)
            duration: duration of the beep (integer) in milliseconds
        """
        if(self._Lock()):
            try:
                freq = abs(int(freq)) & 0xFFFF
                duration = abs(int(duration)) & 0XFFFF
                packet = bytearray(self.PACKET_LENGTH)
                packet[0] = 0x03
                packet[1] = (freq >> 8)
                packet[2] = (freq & 0xFF)
                packet[3] = (duration >> 8)
                packet[4] = (duration & 0xFF)
                self._SendCommand(packet)
                time.sleep(duration/1000.0)
            except serial.SerialTimeoutException:
                self._Debug('RoboBase.Beep: SerialTimeoutException')
            except serial.SerialException:
                self._Debug('RoboBase.Beep: SerialException')
            except:
                self._Debug('RoboBase.Beep: Unexpected Exception')
            self._Unlock()

    def GetInfo(self):
        """Get robot information

        Returns:
            Information about the robot
        """
        r = ''
        if(self._Lock()):
            try:
                packet = bytearray(self.PACKET_LENGTH)
                packet[0] = 0x04
                self._SendCommand(packet)
                r = self._ReadLine()
            except serial.SerialTimeoutException:
                self._Debug('RoboBase.GetInfo: SerialTimeoutException')
            except serial.SerialException:
                self._Debug('RoboBase.GetInfo: SerialException')
            except:
                self._Debug('RoboBase.GetInfo: Unexpected Exception')
            self._Unlock()
        return r

    ###################################################################
    def _ReadLine(self):
        return self._ser.readline()

    def _ReadBytes(self, n):
        return self._ser.read(n)

    def _Read1UByte(self):
        return ord(self._ser.read(1))

    def _Read2UBytes(self):
        return (ord(self._ser.read(1)) << 8) + ord(self._ser.read(1))
