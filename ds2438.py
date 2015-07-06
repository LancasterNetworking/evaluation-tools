#!/usr/bin/python
from struct import *
import glob
import os
import sys
import subprocess
import time
import math


crc_lookup_table = [
		0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
		157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
		35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
		190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
		70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
		219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
		101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
		248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
		140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
		17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
		175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
		50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
		202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
		87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
		233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
		116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53
		]


def open_dev():
	try:
		if subprocess.check_call(['modprobe', 'w1_gpio'], stdin=None, stdout=None, stderr=None, shell=False) != 0:
			print "Failed to modprobe"
			return None
	except:
		print "Failed to modprobe"
		return None
	pdev = glob.glob('/sys/bus/w1/devices/26*')
	if len(pdev) <= 0:
		print 'Didnt find ds2438'
		return None
	path = pdev[0]
	if path is not None:
		dev = os.open(''.join([str(path), '/rw']), os.O_RDWR)
		return dev
	else:
		return None


def get_current(device):
	buff = read_dev(device, 0x00)
	if buff is None:
		return str(0.00)
	if len(buff) > 8:
		return str(math.fabs(convert_bytes(buff[5], buff[6])/(4096.0 * 0.050)))


def read_dev(device, page):

	attempts = 1
	buff = pack('BB', 0xB8, page)
	os.write(device, buff)
	buff = pack('BB', 0xBE, page)

	for idx in range(0, attempts):
		os.write(device, buff)
		out = os.read(device, 9)
		out = unpack('BBBBBBBBB', out)
		#print "Out: " + str(out)
		if check_crc(out, 8) is True:
			return out
		else:
			time.sleep(0.01)
			pass
	return None


def convert_bytes(lsb, msb):
	result = (msb << 8) | lsb

	if result >= 32768:
		#print "Result: " + str(~result)
		return ((~result) & 0xFFFF)+1;
	else:
		#print "Less than 32768"
		return result;


def check_crc(buff, length):
	crc = 0
	for b in buff[:-1]:
		crc = crc_lookup_table[crc ^ int(b)]
	if crc == buff[length]:
		return True
	else:
		return False


if __name__ == '__main__':
	os.system('modprobe w1-gpio')
	d = open_dev()
	if len(sys.argv) == 2:
		for i in range(0, int(sys.argv[1])):
			print get_current(d)
			time.sleep(1.00)
	else:
		while True:
			print get_current(d)
			time.sleep(1.00)
