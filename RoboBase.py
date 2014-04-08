#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import threading
import struct
import time

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


	def _SendCommand(self, cmd, *args):
		params = ''.join(args)
		packet = (chr(cmd) + params + ' '*self.PACKET_LENGTH)[:self.PACKET_LENGTH]
		self.ser.write(packet)
		self.ser.flush()
		r = self.ser.read(self.PACKET_LENGTH)
		if(packet != r):
			self._Debug('Packet Mismatch')
			self._Debug(map(ord,packet))
			self._Debug(map(ord,r))


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
				self._SendCommand(0x01, self._Pack1UByte(m1_dir), self._Pack1UByte(abs(int(motor1)) & 0xFF),
										self._Pack1UByte(m2_dir), self._Pack1UByte(abs(int(motor2)) & 0XFF))
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
				t0 = time.time()
				self._SendCommand(0x02, self._Pack2UBytes(abs(int(max_distance)) & 0xFFFF))
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
				self._SendCommand(0x03, self._Pack2UBytes(abs(int(freq)) &0xFFFF), self._Pack2UBytes(abs(int(duracion)) & 0XFFFF))
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
				self._SendCommand(0x04)
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


	def _Read1Byte(self):
		return struct.unpack(">b", self.ser.read(1))[0]


	def _Read1UByte(self):
		return struct.unpack(">B", self.ser.read(1))[0]


	def _Read2Bytes(self):
		return struct.unpack(">h", self.ser.read(2))[0]


	def _Read2UBytes(self):
		return struct.unpack(">H", self.ser.read(2))[0]


	def _Read4Bytes(self):
		return struct.unpack(">i", self.ser.read(4))[0]


	def _Read4UBytes(self):
		return struct.unpack(">I", self.ser.read(4))[0]


	def _Pack1Byte(self, n):
		return struct.pack(">b", n)


	def _Pack1UByte(self, n):
		return struct.pack(">B", n)


	def _Pack2Bytes(self, n):
		return struct.pack(">h", n)


	def _Pack2UBytes(self, n):
		return struct.pack(">H", n)


	def _Pack4Bytes(self, n):
		return struct.pack(">i", n)


	def _Pack4UBytes(self, n):
		return struct.pack(">I", n)


if __name__=="__main__":
	rob = RoboBase("/dev/rfcomm0")
	print rob.GetInfo()
	#print time.time()
	#rob.Beep(440, 500)
	#print time.time()
	for i in range(50):
		print rob.Ping(500)
	#rob.SetMotors(-255, 255)
	#time.sleep(2)
	#rob.SetMotors(0, 0)
	rob.Close()
