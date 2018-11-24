#################################################
# Ligh L16 stress module test                   #
# current version V0.01                         #
# Light.co                                      #
# MAMO SARGSYAN                                 #
#################################################

import subprocess
import time
from time import strftime, localtime
import re
from adbandroid import adb_android
import sys


class StressTest:

	def __init__(self):
		self.channel_sel = "-m 0 -s 0 -w -p"
		self.com_tran_id = " 00"
		self.mod_mir_mov_bitmask = " 00 45 00 C0 7D 00"
		self.hs2_bit = " 00 40"
		self.hs1_bit = " 00 00"
		self.mod_lens_bitmask = " 00 41 00 C0 FF 01"
		self.stop = False
		self.dev_list = []
		self.adb_dev_id = self.connect()
		print self.adb_dev_id
		self.copy_lcc()
		self.copy_prog_app()

	def connect(self):
		print "Trying to connect..."
		"""
		1. verify pluged in android devieces
		2. let user  to choose which device will be used
		:return: device ID
		"""
		raw_devs_list = adb_android.devices()[-1].split("\r")
		if "offline" in raw_devs_list[1].lower():
			print "Device offline unable to porsue"
			exit("device offline")
		try:
			for items in raw_devs_list:
				try:
					if re.search("\n(\S)", items):
						self.adb_dev_id = re.search("\n(\S+)\t", items).group(1)
						self.dev_list.append(self.adb_dev_id)
				except RuntimeError:
					raise "Unable to find any capatible devices"

			# if len(self.dev_list) > 1:
			# 	dev_list_index = raw_input \
			# 		("There are more than one device connected to the host. Which one to use?: ")
			# 	while not self.dev:
			# 		for devices in dev_list_index:
			# 			while dev_list_index != devices[-3:]:
			# 				dev_list_index = raw_input("Please verify your input: ")
			#
			# 	while int(dev_list_index) - 1 > len(self.dev_list) - 1 or int(dev_list_index) < 1:
			# 		time.sleep(0.5)
			# 		dev_list_index = raw_input("Please verify your input: ")
			# 		self.dev_list.sort()
			# 		self.dev = self.dev_list[int(dev_list_index) - 1]
			# elif len(self.dev_list) == 1:
			return self.adb_dev_id
		except:
			raise sys.exit("No device connected or unknown error")

		return self.adb_dev_id

	def get_local_time(self):
		pass

	def send_command(self, command, timestamp=False, extra_param=False):
		process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
		raw_out = process.communicate()[0]
		raw_out = str(raw_out).split("\r")[0]
		if raw_out is not None:
			if timestamp is False:
				return raw_out
			elif timestamp:
				return self.get_local_time(), raw_out

	def asic_reset(self):
		print "resetting"
		self.send_command('adb -s {} shell /data/prog_app_p2 -q'.format(self.adb_dev_id))

	def copy_lcc(self):
		print "Copying lcc..."
		self.send_command('adb shell -s {} "cp /etc/lcc /data/; chmod 777 /data/lcc"'.format(self.adb_dev_id))

	def copy_prog_app(self):
		print "Copying prog_app_p2..."
		cmd = 'adb -s {} shell "cp /etc/prog_app_p2 /data/; chmod 777 /data/prog_app_p2"'.format(self.adb_dev_id)
		copy_return = self.send_command(cmd)
		if not "errors" in copy_return:
			print "prog_app_p2 is copied"
		else:
			print "Error while copyying prog_app_p2"

	def move_mirrors(self):
		cmd = 'adb -s {} shell "./data/lcc {}"'.format((self.adb_dev_id), (self.channel_sel + self.com_tran_id +
		       self.mod_mir_mov_bitmask + self.hs1_bit*8))
		self.send_command(cmd)
		time.sleep(0.5)
		cmd = 'adb -s {} shell "./data/lcc {}"'.format((self.adb_dev_id), (self.channel_sel + self.com_tran_id + self.mod_mir_mov_bitmask + self.hs2_bit * 8))
		self.send_command(cmd)

	def move_lenses(self):
		cmd = 'adb -s {} shell "./data/lcc {}"'.format((self.adb_dev_id),\
				(self.channel_sel + self.com_tran_id +
				self.mod_lens_bitmask + self.hs1_bit * 11))
		self.send_command(cmd)
		time.sleep(0.5)
		cmd = 'adb -s {} shell "./data/lcc {}"'\
			.format(self.adb_dev_id, (self.channel_sel + self.com_tran_id
		                              + self.mod_lens_bitmask + self.hs2_bit * 11))
		self.send_command(cmd)

	def read_battery_capcaity(self):
		cmd = 'adb -s {} shell "cat ./sys/class/power_supply/battery/capacity"'.format(self.adb_dev_id)
		level = self.send_command(cmd)
		if int(level) < 11:
			print "Battery charge level is critical:  " + level.rstrip() + "%"
		return int(level)

	def do_charge(self, need_charge):
		verify_status_cmd = 'adb -s {} shell ' \
		                    '"cat /sys/class/power_supply/battery/charging_enabled"'.format(self.adb_dev_id)
		if need_charge:
		# enable charging
			cmd = 'adb -s {} shell "echo 1 > ./sys/class/power_supply/battery/charging_enabled"'\
				.format(self.adb_dev_id)
			self.send_command(cmd)
			self.charging_status = self.send_command(verify_status_cmd)
			if self.charging_status == str(1):
				print "Charging enabled successfully"
		# disable charging
		elif self.send_command(verify_status_cmd) == str(1):
			cmd = 'adb -s {} shell "setprop persist.fih.flight_flag 0"'.format(self.adb_dev_id)
			self.send_command(cmd)
			time.sleep(0.2)
			cmd = 'adb -s {} shell "echo 0 > ./sys/class/power_supply/battery/charging_enabled"' \
			 	.format(self.adb_dev_id)
			self.send_command(cmd)
			self.charging_status = self.send_command(verify_status_cmd)
			if  self.charging_status == str(0):
				print "Charging disabled"

	def run_test(self):
		st_time = time.time()
		cycle_count = 0
		self.asic_reset()
		while not self.stop:
			self.move_lenses()
			self.move_mirrors()
			time.sleep(1)
			cycle_count += 1
			if cycle_count % 10 == 0:
				print "%d cycles are done" % cycle_count
				print "%d minutes are passed" % ((time.time() - st_time) / 60)
				self.asic_reset()
				time.sleep(1)
			if cycle_count == 50:
				self.stop = True
				print "50k cycles are done at ", \
					strftime("%H:%M:%S", localtime())
			if self.read_battery_capcaity() < 10:
				while self.read_battery_capcaity() < 50:
					self.do_charge(True)
					time.sleep(300)



dut = StressTest()
dut.run_test()
