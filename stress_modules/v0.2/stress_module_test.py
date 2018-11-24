#################################################
# Ligh L16 stress module test                   #
# current version V0.01                         #
# Light.co                                      #
# MAMO SARGSYAN
# V 0.1                                 #
#################################################

import subprocess
import time
from time import strftime, localtime
import re
import sys

# debug = True
debug = False


class StressTest:
	def __init__(self):
		self.channel_sel_write = "-m 0 -s 0 -w -p"
		self.channel_sel_read = "-m 0 -s 0 -r -p"
		self.tran_id = " 00 00"
		self.mir_move_com_id = " 45 00"
		self.mir_pos_com_id = " 44 00"
		self.lens_move_com_id = " 41 00"
		self.lens_pos_com_id = " 40 00"
		self.all_mir_read_bitmask = " C0 FF 01"
		self.all_mir_bitmask = " C0 7D 00"
		self.hs2_bit = " 00 40"
		self.hs1_bit = " 00 00"
		self.all_lens_bitmask = " C0 FF 01"
		self.stop = False
		self.dev_list = []
		self.adb_device_id = None
		self.adb_device_id = self.connect()
		self.copy_lcc()
		self.copy_prog_app()
		self.cycle_count = 1
		self.all_mirr_data = None
		self.mir_result = {}
		self.lens_result = {}
		self.file_ref = None

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
				dev_list_index = raw_input \
					("There are more than one device connected to the host. Which one to use?: ")
				while not self.adb_device_id:
					while int(dev_list_index) == 0 or int(dev_list_index) > len(dev_list):
						dev_list_index = raw_input("Please verify your input: ")
						time.sleep(0.5)
					self.adb_device_id = dev_list[int(dev_list_index) - 1]
				return self.adb_device_id
			elif len(dev_list) == 1:
				return dev_list[0]

	def get_local_time(self):
		pass

	def send_command(self, command, timestamp=False, extra_param=False):
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
		print "Copying lcc..."
		self.send_command('adb  -s {} shell "cp /etc/lcc /data/; chmod 777 /data/lcc"'.format(self.adb_device_id))

	def copy_prog_app(self):
		#  print "Copying prog_app_p2..."
		cmd = 'adb -s {} shell "cp /etc/prog_app_p2 /data/; chmod 777 /data/prog_app_p2"'.format(self.adb_device_id)
		copy_return = self.send_command(cmd)
		if not "errors" in copy_return:
			if debug:
				print "prog_app_p2 is copied"
		else:
			print "Error while copyying prog_app_p2"

	def move_mirrors(self):
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format(self.adb_device_id,
		            (self.channel_sel_write + self.tran_id + self.mir_move_com_id +
		             self.all_mir_bitmask + self.hs1_bit * 8))
		self.send_command(cmd)
		mirr_data_1 = self.read_mirr_position(1)
		time.sleep(0.2)
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format((self.adb_device_id),
		            (self.channel_sel_write + self.tran_id + self.mir_move_com_id +
		             self.all_mir_bitmask + self.hs2_bit * 8))
		self.send_command(cmd)
		mirr_data_2 = self.read_mirr_position(2)
		self.all_mirr_data = mirr_data_1 + mirr_data_2

	def move_lenses(self):
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format((self.adb_device_id),
		            (self.channel_sel_write + self.tran_id + self.lens_move_com_id +
		             self.all_lens_bitmask + self.hs1_bit * 11))
		self.send_command(cmd)
		lens_data_1 = self.read_lens_position(1)
		time.sleep(0.2)
		cmd = 'adb -s {} shell "./data/lcc {}"' \
			.format(self.adb_device_id, (self.channel_sel_write + self.tran_id + self.lens_move_com_id +
		                                 self.all_lens_bitmask + self.hs2_bit * 11))
		self.send_command(cmd)
		lens_data_2 = self.read_lens_position(2)
		self.all_lens_data = lens_data_1 + lens_data_2

	# print "all lens data", self.all_lens_data

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
		all_mirr_pos = ('adb -s {} shell "./data/lcc {}"'
		                .format(self.adb_device_id, (self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
		                                             self.all_mir_bitmask)))
		mirr_possitions = self.send_command(all_mirr_pos)
		if hs == 1:
			self.mirr_possitions = [1] + ["".join([i.strip() for i in mirr_possitions])]
		elif hs == 2:
			self.mirr_possitions = [2] + ["".join([i.strip() for i in mirr_possitions])]
		return self.mirr_possitions

	# print "reading mirr possitions", possitions

	def read_lens_position(self, hs):
		all_lens_pos = ('adb -s {} shell "./data/lcc {}"'
		                .format(self.adb_device_id, (self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
		                                             self.all_lens_bitmask)))
		lens_possitions = self.send_command(all_lens_pos)
		if hs == 1:
			self.lens_possitions = [1] + ["".join([i.strip() for i in lens_possitions])]
		elif hs == 2:
			self.lens_possitions = [2] + ["".join([i.strip() for i in lens_possitions])]
		return self.lens_possitions

	# print "reading  lens possitions", possitions

	def calculate_possitions(self, data, mir_or_len):
		s = 0
		e = s + 2
		lens_mod_list_hs1 = ['HS1', 'B1_1', 'B2_1', 'B3_1', 'B4_1', 'B5_1', 'C1_1',
		                     'C2_1', 'C3_1', 'C4_1', 'C5_1', 'C6_1']
		lens_mod_list_hs2 = ['HS2', 'B1_2', 'B2_2', 'B3_2', 'B4_2', 'B5_2', 'C1_2',
		                     'C2_2', 'C3_2', 'C4_2', 'C5_2', 'C6_2']
		mirr_mod_list_hs1 = ['HS1', 'B1_1', 'B2_1', 'B3_1', 'B5_1', 'C1_1', 'C2_1', 'C3_1',
		                   'C4_1']
		mirr_mod_list_hs2 = ['HS2', 'B1_2', 'B2_2', 'B3_2', 'B5_2', 'C1_2', 'C2_2', 'C3_2',
		                   'C4_2']
		lens_mod_list = lens_mod_list_hs1 + lens_mod_list_hs2
		mirr_mod_list = mirr_mod_list_hs1 + mirr_mod_list_hs2
		if mir_or_len == 1:  # mirror
			for item in mirr_mod_list:  # lens mod  pos  cobined 2 list of modules with HS1 + HS2
				if item == "HS1":
					data_index = 1
					continue
				if item == "HS2":
					data_index = 3
					s, e = 0, 2
					continue
				hx1 = data[data_index][s:e]
				s += 2
				e += 2
				hx2 = data[data_index][s:e]
				s += 2
				e += 2
				if hx1 and hx2:
					value = self.convert_hex_to_dec((hx2 + hx1))
					self.mir_result[item] = value
			s, e = 0, 2
			return self.mir_result
		if mir_or_len == 2:  # lens
			for item in lens_mod_list:  # lens mod  pos  coMbined 2 list of modules with HS1 + HS2
				if item == "HS1":
					data_index = 1
					continue
				if item == "HS2":
					data_index = 3
					s, e = 0, 2
					continue
				hx1 = data[data_index][s:e]
				s += 2
				e += 2
				hx2 = data[data_index][s:e]
				s += 2
				e += 2
				if hx1 and hx2:
					value = self.convert_hex_to_dec((hx2 + hx1))
					self.lens_result[item] = value
			s, e = 0, 2
			return self.lens_result
		# print "mir_res", self.mir_result
		# print "lens result dit", self.lens_result

	def convert_hex_to_dec(self, hx_data):
		return int(hx_data, 16)

	def record_data_header(self):
		self.file_ref = open((self.adb_device_id + "_actuator_log.csv"), "a+")
		lens_log_header_1 = "B1_1,B2_1,B3_1,B4_1,B5_1,C1_1,C2_1,C3_1,C4_1,C5_1,C6_1"
		lens_log_header_2 = "B1_2,B2_2,B3_2,B4_2,B5_2,C1_2,C2_2,C3_2,C4_2,C5_2,C6_2"
		mirr_log_header_1 = "B1_1,B2_1,B3_1,B5_1,C1_1,C2_1,C3_1,C4_1"
		mirr_log_header_2 = "B1_2,B2_2,B3_2,B5_2,C1_2,C2_2,C3_2,C4_2"
		self.all_header = "N," + lens_log_header_1 + ",," + lens_log_header_2 + ",," + \
		                  mirr_log_header_1 + ",," + "," + mirr_log_header_2 + ",\n"
		self.file_ref.write(self.all_header)
		self.file_ref.close()

	def record_data(self, data):
		if len(data) > 0:
			lens_res_keys = data.keys()
			lens_res_keys.sort()
			temp_row = ""
			for i in self.all_header.split(",")[:27]:
				if i != '' and not "HS" in i and len(i) > 1 and not "N" in i:
					temp_row = temp_row + str((data[i])) + ","
				else:
					temp_row = temp_row + ","
			for i_1 in self.all_header.split(",")[27:]:
				if i_1 != '' and not "HS" in i_1 and len(i_1) > 1 and not "N" in i:
					temp_row = temp_row + str((data[i_1])) + ","
				else:
					temp_row = temp_row + ","
			temp_row = str(self.cycle_count) + temp_row + "\n"
			self.file_ref.write(temp_row)

	def run_test(self):
		self.record_data_header()
		st_time = time.time()
		self.asic_reset()
		self.move_lenses()
		self.move_mirrors()
		while not self.stop:
			self.file_ref = open((self.adb_device_id + "_actuator_log.csv"), "a+")
			time.sleep(0.2)
			self.move_lenses()
			data = self.calculate_possitions(self.all_lens_data, 2)
			self.move_mirrors()
			self.calculate_possitions(self.all_mirr_data, 1)
			time.sleep(0.5)
			self.record_data(data)
			self.cycle_count += 1
			if self.cycle_count % 10 == 0:
				print "%d cycles are done" % self.cycle_count
				print "%d minutes are passed" % ((time.time() - st_time) / 60)
				self.asic_reset()
				time.sleep(0.3)
				self.file_ref.close()
			if self.cycle_count == 50000:
				self.stop = True
				print "50k cycles are done at ", \
					strftime("%H:%M:%S", localtime())
			if self.read_battery_capcaity() < 10:
				self.stop = True
				if not self.file_ref.closed:
					self.file_ref.close()
				print "Test is stop due critical battery, file saved"
			# if self.read_battery_capcaity() < 10:
			# 	while self.read_battery_capcaity() < 50:
			# 		self.do_charge(True)
			# 		time.sleep(300)
			self.file_ref.close()


dut = StressTest()
dut.run_test()
