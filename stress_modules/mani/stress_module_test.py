#################################################
# Ligh L16 stress module test                   #
# current version V0.01                         #
# Light.co                                      #
# MAMO SARGSYAN                                 #
# V 0.1                                         #
# first version                                 #
# V 0.2                                         #
# # added delta calculation mirrors and lenses  #
# # added timestamp                             #
# # aded data validation on result              #
#################################################

import subprocess
import time
from time import strftime, localtime
from datetime import datetime

import re

# debug = True
debug = False


class StressTest:
	def __init__(self):
		self.channel_sel_write = "-m 0 -s 0 -w -p"
		self.channel_sel_read = "-m 0 -s 0 -r -p"
		self.tran_id = " 00 00"
		self.mir_move_com_id = " 45 80"
		self.mir_pos_com_id = " 44 00"
		self.lens_move_com_id = " 41 80"
		self.lens_pos_com_id = " 40 00"
		self.all_mir_bitmask = " C0 7D 00"
		self.B1_mod_bitmask = " 40 00 00"
		self.hs2_bit = " 00 40"
		self.hs1_bit = " 00 00"
		self.all_lens_bitmask = " C0 FF 01"
		self.stop = False
		self.dev_list = []
		self.adb_device_id = None
		self.adb_device_id = self.connect
		self.copy_lcc()
		self.copy_prog_app()
		self.cycle_count = 1
		self.all_mirr_data = None
		self.mir_result = {}
		self.lens_result = {}
		self.file_ref = None
		self.all_lens_data = None
		self.all_mirr_data = None

	@ property
	def connect(self):
		print "Trying to connect..."
		"""
		1. verify pluged in android devieces
		2. let user  to choose which device will be used
		:return: device ID
		"""
		raw_devs = self.send_command("adb devices")
		dev_list = re.findall("LFCL\S+", raw_devs)
		if len(dev_list) < 1:
			exit("No device found")
		else:
			dev_list.sort()
			print "Attached devices", dev_list
			if len(dev_list) > 1:
				dev_list_index = raw_input\
					("There are more than one device connected to the host. Which one to use?: ")
				while not self.adb_device_id:
					while int(dev_list_index) == 0 or int(dev_list_index) > len(dev_list):
						dev_list_index = raw_input("Please verify your input: ")
						time.sleep(0.5)
					self.adb_device_id = dev_list[int(dev_list_index) - 1]
				return self.adb_device_id
			elif len(dev_list) == 1:
				raw_input("Confirm if you want to connect to this {} \n press Enter "
					.format(dev_list[0]))
				return dev_list[0]

	def curr_time(self):
		return (datetime.now().strftime("%H:%M:%S.%f")[:-3])



	def send_command(self, command, timestamp=False):
		process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
		raw_out = process.communicate()[0]
		raw_out = " ".join(raw_out.split())
		if raw_out is not None:
			if timestamp is False:
				return raw_out
			elif timestamp:
				return self.get_local_time(), raw_out

	def asic_reset(self):
		print "resetting"
		self.send_command('adb -s {} shell /data/prog_app_p2 -q'.format(self.adb_device_id))

	def copy_lcc(self):
		#  print "Copying lcc..."
		command_return = self.send_command('adb  -s {} shell "cp /etc/lcc /data/; chmod 777 /data/lcc"'
		                                   .format(self.adb_device_id))
		if not "errors" in command_return:
			if debug:
				print "LCC is copied"
		else:
			print "Error while copyying LCC"

	def copy_prog_app(self):
		#  print "Copying prog_app_p2..."
		cmd = 'adb -s {} shell "cp /etc/prog_app_p2 /data/; chmod 777 /data/prog_app_p2"'.format(self.adb_device_id)
		command_return = self.send_command(cmd)
		if not "errors" in command_return:
			if debug:
				print "prog_app_p2 is copied"
		else:
			print "Error while copyying prog_app_p2"

	def move_mirrors(self):
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format(self.adb_device_id,
				(self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					self.B1_mod_bitmask + self.hs1_bit * 1))
		self.send_command(cmd)


	def move_lenses(self):
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format((self.adb_device_id),
						(self.channel_sel_write + self.tran_id + self.lens_move_com_id +
							self.all_lens_bitmask + self.hs1_bit * 11))
		self.send_command(cmd)

	def read_battery_capcaity(self):
		cmd = 'adb -s {} shell "cat ./sys/class/power_supply/battery/capacity"'.format(self.adb_device_id)
		level = self.send_command(cmd)
		if int(level) < 11:
			print "Battery charge level is critical:  " + level.rstrip() + "%"
		return int(level)

	def do_charge(self, need_charge):
		verify_status_cmd = 'adb -s {} shell ' \
			'"cat /sys/class/power_supply/battery/charging_enabled"'.format(self.adb_device_id)
		if need_charge:
			# enable charging
			cmd = 'adb -s {} shell "echo 1 > ./sys/class/power_supply/battery/charging_enabled"' \
				.format(self.adb_device_id)
			self.send_command(cmd)
			self.charging_status = self.send_command(verify_status_cmd)
			if self.charging_status == str(1):
				print "Charging enabled successfully"
		# disable charging
		elif self.send_command(verify_status_cmd) == str(1):
			cmd = 'adb -s {} shell "setprop persist.fih.flight_flag 0"'.format(self.adb_device_id)
			self.send_command(cmd)
			time.sleep(0.2)
			cmd = 'adb -s {} shell "echo 0 > ./sys/class/power_supply/battery/charging_enabled"' \
				.format(self.adb_device_id)
			self.send_command(cmd)
			self.charging_status = self.send_command(verify_status_cmd)
			if self.charging_status == str(0):
				print "Charging disabled"

	def read_mirr_position(self, hs):
		"""
		:param hs: hard stop 1 or 2
		:return: hard stop pos tag + 16 bit mirr position data
		"""
		all_mirr_pos = ('adb -s {} shell "./data/lcc {}"'
			.format(self.adb_device_id, (self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
				self.B1_mod_bitmask)))
		mirr_possitions = self.send_command(all_mirr_pos)
		if hs == 1:
			mirr_possitions = [1] + ["".join([i.strip() for i in mirr_possitions])]
		elif hs == 2:
			mirr_possitions = [2] + ["".join([i.strip() for i in mirr_possitions])]
		return mirr_possitions

	def read_lens_position(self, hs):
		"""
		:param hs: hard stop 1 or 2
		:return: hard stop pos tag + 22 bit lens position data
		"""
		all_lens_pos = ('adb -s {} shell "./data/lcc {}"'
		                .format(self.adb_device_id, (self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
		                                             self.B1_mod_bitmask)))
		lens_possitions = self.send_command(all_lens_pos)
		if hs == 1:
			lens_possitions = [1] + ["".join([i.strip() for i in lens_possitions])]
		elif hs == 2:
			lens_possitions = [2] + ["".join([i.strip() for i in lens_possitions])]
		return lens_possitions

	def calculate_possitions(self, data, mir_or_len):
		"""
		:param data: for mirrors [0, "45100012000456078009800F011A0100", 1, 45100012000456078009800F011A0100]
					 for lenses [0, 32 bit data, 1, 32 bit data]
		:param mir_or_len: 1 mirror 2 lens
		:return:
		"""
		s = 0
		e = s + 2
		if mir_or_len == 1:  # mirror
			hx1 = data[1][s:e]
			s += 2
			e += 2
			hx2 = data[1][s:e]
			s += 2
			e += 2
			try:
				value = self.convert_hex_to_dec((hx2 + hx1))
			except:
				value = "--"

			return value
		if mir_or_len == 2:  # lens
			hx1 = data[1][s:e]
			s += 2
			e += 2
			hx2 = data[1][s:e]
			s += 2
			e += 2
			try:
				value = self.convert_hex_to_dec((hx2 + hx1))
			except:
				value = "--"
			return value

	def convert_hex_to_dec(self, hx_data):
		return int(hx_data, 16)

	def run_test(self):
		print "{} device is selected".format(self.adb_device_id)
		st_time = time.time()
		self.asic_reset()
		self.move_lenses()
		self.move_mirrors()
		while not self.stop:
			lens_data_1 = self.read_lens_position(1)
			print "lense hard stop pos. ", self.calculate_possitions(lens_data_1, 2)
			mirr_data_1 = self.read_mirr_position(1)
			print "Mirror hard stop pos. ", self.calculate_possitions(mirr_data_1, 1)
			time.sleep(0.1)
			if self.cycle_count % 10 == 0:
				print "%d cycles are done" % self.cycle_count
				print "%d minutes are passed" % ((time.time() - st_time) / 60)
				self.asic_reset()
				time.sleep(0.3)
				self.file_ref.close()
			if self.cycle_count == 100:
				self.stop = True
				print "{} cycles are done at ".format(str(self.cycle_count)), \
					strftime("%H:%M:%S", localtime())
			if self.read_battery_capcaity() < 10:
				#self.stop = True
				if not self.file_ref.closed:
					self.file_ref.close()
				print "Test is stop due critical battery, file saved"
			if self.read_battery_capcaity() < 10:
				while self.read_battery_capcaity() < 50:
					self.do_charge(True)
					time.sleep(300)


dut = StressTest()
dut.run_test()
