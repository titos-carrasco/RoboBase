#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import threading
import time
import struct

class RoboBase:
	PACKET_LENGTH = 8;

	def __init__(self, port, bauds=9600):
		self.lock = threading.Lock()
		self.ser = None
		for t in range(4):
			try:
				self.ser = serial.Serial(port, baudrate=bauds, bytesize=8, parity='N', stopbits=1, timeout=3)
				self._Debug('RoboBase.Init: Conectado en %s a %d bps' % (port, bauds))
				self._Debug('RoboBase.Init: Consumiendo data antigua')
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
		if(self.IsConnected()):
			self._ConsumeOldData()


	def _Lock(self):
		self.lock.acquire()


	def _Unlock(self):
		self.lock.release()


	def _Debug(self, val):
		print val


	def _ConsumeOldData(self):
		timeout = self.ser.timeout
		self.ser.timeout = 1
		while(True):
			try:
				self.ser.read(1000)
			finally:
				break
		self.ser.timeout = timeout


	def IsConnected(self):
		if(self.ser==None):
			return False
		else:
			return self.ser.isOpen()


	def Close(self):
		if(not self.IsConnected()):
			return

		self._Lock()
		self.ser.close()
		self.ser = None
		self._Unlock()
		self.lock = None


	def _SendCommand(self, packet):
		self.ser.write(packet)
		self.ser.flush()
		r = self.ser.read(self.PACKET_LENGTH)
		if(packet != bytearray(r)):
			self._Debug('Packet Mismatch')
			self._Debug(packet)
			self._Debug(map(ord(r)))


	def SetMotors(self, motor1, motor2):
		if(self.IsConnected()):
			self._Lock()
			try:
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
				packet[2] = abs(int(motor1)) & 0xFF
				packet[3] = m2_dir
				packet[4] = abs(int(motor2)) & 0XFF
				self._SendCommand(packet)
			except serial.SerialTimeoutException:
				self._Debug('RoboBase.SetMotors: SerialTimeoutException')
			except serial.SerialException:
				self._Debug('RoboBase.SetMotors: SerialException')
			finally:
				self._Unlock()


	def Ping(self, max_distance):
		r = 0
		if(self.IsConnected()):
			self._Lock()
			try:
				max_distance = abs(int(max_distance)) & 0xFFFF
				packet = bytearray(self.PACKET_LENGTH)
				packet[0] = 0x02
				packet[1] = (max_distance >> 8)
				packet[2] = (max_distance & 0xFF)
				t0 = time.time()
				self._SendCommand(packet)
				r = self._Read2UBytes()/100.0
			except serial.SerialTimeoutException:
				self._Debug('RoboBase.Ping: SerialTimeoutException')
			except serial.SerialException:
				self._Debug('RoboBase.Ping: SerialException')
			finally:
				self._Unlock()
		return r


	def Beep(self, freq, duracion):
		if(self.IsConnected()):
			self._Lock()
			try:
				freq = abs(int(freq)) & 0xFFFF
				duracion = abs(int(duracion)) & 0XFFFF
				packet = bytearray(self.PACKET_LENGTH)
				packet[0] = 0x03
				packet[1] = (freq >> 8)
				packet[2] = (freq & 0xFF)
				packet[3] = (duracion >> 8)
				packet[4] = (duracion & 0xFF)
				self._SendCommand(packet)
				time.sleep(duracion/1000.0)
			except serial.SerialTimeoutException:
				self._Debug('RoboBase.Beep: SerialTimeoutException')
			except serial.SerialException:
				self._Debug('RoboBase.Beep: SerialException')
			finally:
				self._Unlock()


	def GetInfo(self):
		r = ''
		if(self.IsConnected()):
			self._Lock()
			try:
				packet = bytearray(self.PACKET_LENGTH)
				packet[0] = 0x04
				self._SendCommand(packet)
				r = self._ReadLine()
			except serial.SerialTimeoutException:
				self._Debug('RoboBase.Beep: SerialTimeoutException')
			except serial.SerialException:
				self._Debug('RoboBase.Beep: SerialException')
			finally:
				self._Unlock()
		return r

	###################################################################

	def _ReadLine(self):
		return self.ser.readline()


	def _ReadBytes(self, n):
		return self.ser.read(n)


	def _Read1UByte(self):
		return ord(self.ser.read(1))


	def _Read2UBytes(self):
		return (ord(self.ser.read(1)) << 8) + ord(self.ser.read(1))


if __name__=="__main__":
	rob = RoboBase("/dev/rfcomm0")
	print rob.GetInfo()
	#print time.time()
	#rob.Beep(440, 500)
	#print time.time()
	for i in range(5):
		print rob.Ping(500)
	#rob.SetMotors(-255, 255)
	#time.sleep(2)
	#rob.SetMotors(0, 0)
	rob.Close()
