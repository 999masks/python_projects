#################################################
# Ligh L16 stress module test                   #
# current version V0.8                         #
# Light.co                                      #
# MAMO SARGSYAN                                 #
# V 0.1                                         #
# first version                                 #
# V 0.2                                         #
# # added delta calculation mirrors and lenses  #
# # added timestamp                             #
# # aded data validation on result              #
# V 0.3                                         #
# # added temperature reading                   #
# V 0.4                                         #
# # added keyboard interupt to stop the test    #
# # added move lenses to desired hs at the end  #
# V 0.5                                         #
# # data validation before doing calculation    #
# # added raw data output for verification      #
# V 0.6                                         #
# # added automatic stop if 10 failures happens #
# V 0.7                                         #
# # added UI                                    #
# # plotting functions                          #
# # separate charts for mirror and lenses       #
# # drop down menu to select desired DUT        #
# # live test status on ui                      #
# # added more control buttons                  #
# # arranged buttons layout                     #
# V 0.8                                         #
# # update status on UI                         #
# # separate graph on mirrors and lenses        #
# V 0.9                                         #
# # add A module move and position read         #
# # A module selection on UI                    #
# # more messages on UI                         #
# #
# #  d A module move and position read          #
# # add A module move and position read         #
# V 0.10                                        #
# # selective run for each type of actuator     #
# # log output ajduted acording run type        #
# # change run mode on the fly, without reopen  #
# # fixed bug related A and lens run calculation#
# #  simplified code, removed separate functions#
# # add A module move and position read         #
#################################################

# TODO implement failure check by defined criteris on the fly
# TODO a reading s are too high
# todo when i add a modules results lensa data getting mixed up

import subprocess
import time
from time import strftime, localtime
from datetime import datetime
import struct
from threading import Thread
from Tkinter import *
from pylab import show
import matplotlib.pyplot as plt

#debug = True
debug = False

def curr_time():
	return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class CycleTest:
	def __init__(self):
		self.current_version = "0.6"
		print "Module test program, version 0.8"
		self.channel_sel_write = "-m 0 -s 0 -w -p"
		self.channel_sel_read = "-m 0 -s 0 -r -p"
		self.tran_id = " 00 00"
		self.mir_move_com_id = " 45 80"
		self.mir_pos_com_id = " 44 00"
		self.lens_move_com_id = " 41 80"
		self.lens_pos_com_id = " 40 00"
		self.all_mir_bitmask = " C0 7D 00"
		self.hs2_bit = " 00 40"
		self.hs1_bit = " 00 00"
		self.all_lens_bitmask = " C0 FF 01"
		self.A_mod_bitmask = " 3E 00 00"
		self.global_bitmask = " FE FF 01"
		self.A_mod_move_com_id = self.lens_move_com_id
		self.A_mod_pos_com_id = self.lens_pos_com_id
		self.mode_select_VCM = 1
		self.mode_select_lens = 2
		self.mode_select_mirror = 3
		self.mode_select_VCM_lens = 4
		self.hs1 = 1
		self.hs2 = 2
		self.stop = False
		self.is_runing = False
		self.dev_list = []
		self.adb_device_id = None
		self.cycle_count = 0
		self.all_mirr_data = None
		self.mir_result = {}
		self.lens_result = {}
		self.vcm_result = {}
		self.vcm_lense_result = {}
		self.file_ref = None
		self.all_lens_data = None
		self.all_mirr_data = None
		self.charging_status = None
		self.raw_log_file_ref = None
		self.lens_current_cycle = 0
		self.mirror_error_cycles = 0
		#self.vcm_current_cycle = 0  #
		self.lens_delta_header = ['L_B1', 'L_B2', 'L_B3', 'L_B4', 'L_B5', 'L_C1',
										'L_C2', 'L_C3', 'L_C4', 'L_C5', 'L_C6']
		self.mirror_delta_header = ['M_B1', 'M_B2', 'M_B3', 'M_B5', 'M_C1', 'M_C2',
		                            'M_C3', 'M_C4']
		self.vcm_delta_header = ['A1', 'A2', 'A3', 'A4', 'A5']
		self.run_VCM = None
		self.run_L = None
		self.run_M = None
		lens_list_hs1 = [
			'L_B1_1', 'L_B2_1', 'L_B3_1', 'L_B4_1', 'L_B5_1', 'L_C1_1', 'L_C2_1', 'L_C3_1',
			'L_C4_1', 'L_C5_1', 'L_C6_1']
		lens_list_hs2 = [
			'L_B1_2', 'L_B2_2', 'L_B3_2', 'L_B4_2', 'L_B5_2', 'L_C1_2', 'L_C2_2', 'L_C3_2',
			'L_C4_2', 'L_C5_2', 'L_C6_2']
		mirr_list_hs1 = [
			'M_B1_1', 'M_B2_1', 'M_B3_1', 'M_B5_1', 'M_C1_1', 'M_C2_1', 'M_C3_1', 'M_C4_1']
		mirr_list_hs2 = [
			'M_B1_2', 'M_B2_2', 'M_B3_2', 'M_B5_2', 'M_C1_2', 'M_C2_2', 'M_C3_2', 'M_C4_2']
		vcm_header_hs1 = ['A1_1', 'A2_1', 'A3_1', 'A4_1', 'A5_1']
		vcm_header_hs2 = ['A1_2', 'A2_2', 'A3_2', 'A4_2', 'A5_2']
		self.all_vcm_header = vcm_header_hs1 + vcm_header_hs2
		self.all_lens_header = lens_list_hs1 + lens_list_hs2
		self.all_mirr_header = mirr_list_hs1 + mirr_list_hs2
		#  When run VCM and lense, VCM calculation is negative, hense hs2 first then hs1
		self.vcm_lense_header = vcm_header_hs2 + lens_list_hs1 + vcm_header_hs1 + lens_list_hs2
		self.test_data = {}
		self.is_runing = False
		self.delta_header = None
		self.all_header = None

	def get_dev_list(self):
		raw_devs = self.send_command("adb devices")
		self.dev_list = re.findall("LFC\S+", raw_devs)
		return self.dev_list

	def connect(self):
		print "Trying to connect..."
		"""
		1. verify pluged in android devieces
		2. let user  to choose which device will be used
		:return: device ID
		"""
		self.adb_device_id = start_test_gui.tkvar.get()
		return self.adb_device_id

	def read_inputs(self):
		self.run_VCM = start_test_gui.VCM_select_var.get()
		self.run_L = start_test_gui.L_select_var.get()
		self.run_M = start_test_gui.M_select_var.get()
		if self.run_VCM == 1 and self.run_M == 0 and self.run_L == 0:
			self.delta_header = ",".join(self.vcm_delta_header)
		elif self.run_L == 1 and self.run_VCM == 0 and self.run_M == 0:
			self.delta_header = ",".join(self.lens_delta_header)
		elif self.run_M == 1 and self.run_VCM == 0 and self.run_L == 0:
			self.delta_header = ",".join(self.mirror_delta_header)
		elif self.run_VCM == 1 and self.run_L == 1 and self.run_M == 0:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.lens_delta_header)
		elif self.run_VCM == 1 and self.run_M == 1 and self.run_L == 0:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.mirror_delta_header)
		elif self.run_L == 1 and self.run_M == 1 and self.run_VCM == 0:
			self.delta_header = ",".join(self.lens_delta_header) + "," + ",".join(self.mirror_delta_header)
		elif self.run_VCM + self.run_L + self.run_M == 3:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.lens_delta_header) + "," + ",".join(self.mirror_delta_header)
		self.all_header = \
			"N_{},".format(strftime("%m-%d-%Y", localtime())) + "Time" + "," + \
			self.delta_header + "," + "B4 temp." + "\n"

		#  print "vcn state", self.run_VCM, "lense state",  self.run_L, "mirr state", self.run_M
		return (self.run_VCM, self.run_L, self.run_M)

	@staticmethod
	def send_command(command, timestamp=False):
		process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
		raw_out = process.communicate()[0]
		raw_out = " ".join(raw_out.split())
		if raw_out is not None:
			if timestamp is False:
				return raw_out
			elif timestamp:
				return curr_time(), raw_out

	def asic_reset(self):
		print "reseting, s/n-", self.adb_device_id.strip()
		self.send_command('adb -s {} shell /data/prog_app_p2 -q'.format(self.adb_device_id))

	def copy_lcc(self):
		#  print "Copying lcc..."
		command_return = self.send_command(
			'adb  -s {} shell "cp /etc/lcc /data/; chmod 777 /data/lcc"'.format(self.adb_device_id))
		if "errors" not in command_return:
			if debug:
				print "LCC is copied"
		else:
			print "Error while copyying LCC"

	def copy_prog_app(self):
		#  print "Copying prog_app_p2..."
		cmd = 'adb -s {} shell "cp /etc/prog_app_p2 /data/; chmod 777 /data/prog_app_p2"'.format(self.adb_device_id)
		command_return = self.send_command(cmd)
		if "errors" not in command_return:
			if debug:
				print "prog_app_p2 is copied"
		else:
			print "Error while copyying prog_app_p2"

	def multi_module_move(self, mode):
		"""
		:param mode: 1-VCM, 2-Lens, 3- Mirror, 4-VCM and lens
		:return: hs1+hs2 pos list
		"""
		if mode == 1:  # VCM only move
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.A_mod_move_com_id + self.A_mod_bitmask + self.hs2_bit * 5)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_VCM)

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.A_mod_move_com_id + self.A_mod_bitmask + self.hs1_bit * 5)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_VCM)

		elif mode == 2:  # lens only move
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + self.all_lens_bitmask + self.hs1_bit * 11)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_lens)

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + self.all_lens_bitmask + self.hs2_bit * 11)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_lens)

		elif mode == 3:  # mirror only move
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					self.all_mir_bitmask + self.hs1_bit * 8))
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_mirror)
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					self.all_mir_bitmask + self.hs2_bit * 8))
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_mirror)

		elif mode == 4:  # VCM and lens move
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + self.global_bitmask + self.hs1_bit * 16)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_VCM_lens)
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				                    self.lens_move_com_id + self.global_bitmask + self.hs2_bit * 16)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_VCM_lens)
		all_pos = pos_data_1 + pos_data_2
		return all_pos

	def multi_module_pos_read(self, hs, mode):
		if mode == 1:  # read vcm position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.A_mod_pos_com_id
				+ self.A_mod_bitmask)
		elif mode == 2:  # read lens position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id
				+ self.all_lens_bitmask)
		elif mode == 3:  # read mirror positions
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
					self.adb_device_id, (
						self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
						self.all_mir_bitmask))
		elif mode == 4:  # read VCM and lens position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id
				+ self.global_bitmask)
		position_data = self.send_command(cmd)
		if hs == 1:
			position_data = [1] + ["".join([i.strip() for i in position_data])]
		elif hs == 2:
			position_data = [2] + ["".join([i.strip() for i in position_data])]
		return position_data

	def calculate_positions(self, data, mir_len_vcm):
		#  print "data", data
		print "mode", mir_len_vcm
		"""
		:param data: for mirrors [
		0, "45100012000456078009800F011A0100", 1,
		45100012000456078009800F011A0100]
		for lenses [0, 22 byte data, 1, 22 byte data]
		:param mir_len_vcm: 1 mirror 2 lens
		:return: dic {L_B1_1:400', 'L_B2_1:400',..} or dic {M_B3_1:123', 'M_B4_1:322',..}
		"""
		_i = 2
		item = None
		if mir_len_vcm == 1:  # VCM
			if len(data[1]) == 20 and len(data[3]) == 20:
				# print "all vcm header", self.all_vcm_header
				# print "data", data
				for item in self.all_vcm_header[:5]:
					hx1 = data[1][_i - 2:_i]
					_i += 2
					hx2 = data[1][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.vcm_result[item] = value
				_i = 2
				for item in self.all_vcm_header[5:]:
					hx1 = data[3][_i - 2:_i]
					_i += 2
					hx2 = data[3][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.vcm_result[item] = value
				self.vcm_error_cycle = 0
				return self.vcm_result
			else:
				print "wrong VCM data {}".format(item)
				if self.vcm_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				else:
					self.vcm_error_cycle = 0
				return {}

		elif mir_len_vcm == 2:  # lens
			if len(data[1]) == 44 and len(data[3]) == 44:
				for item in self.all_lens_header[:11]:
					hx1 = data[1][_i - 2:_i]
					_i += 2
					hx2 = data[1][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.lens_result[item] = value
				_i = 2
				for item in self.all_lens_header[11:]:
					hx1 = data[3][_i - 2:_i]
					_i += 2
					hx2 = data[3][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.lens_result[item] = value
				self.lens_error_cycles = 0
				return self.lens_result
			else:
				print "wrong lens data {}".format(item)
				if self.lens_error_cycles == 0:
					self.lens_current_cycle = self.cycle_count
				else:
					self.lens_error_cycles = 0
				return {}

		elif mir_len_vcm == 3:  # mirror
			if len(data[1]) == 32 and len(data[3]) == 32:
				for item in self.all_mirr_header[:8]:
					hx1 = data[1][_i - 2:_i]
					_i += 2
					hx2 = data[1][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.mir_result[item] = value
				_i = 2
				for item in self.all_mirr_header[8:]:
					hx1 = data[3][_i - 2:_i]
					_i += 2
					hx2 = data[3][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.mir_result[item] = value
				self.mirror_error_cycles = 0
				return self.mir_result
			else:
				print "wrong mirror data {}".format(item)
				print "cycles:", self.cycle_count
				#  counting wrong data cycles, to stop the test
				if self.mirror_error_cycles == 0:
					self.mirror_error_cycles = self.cycle_count
				else:
					self.mirror_error_cycles = 0
				return {}

		elif mir_len_vcm == 4:  # VCM + Lens
			print  "calcual 4 data", data
			if len(data[1]) == 64 and len(data[3]) == 64:
				#  print "all vcm + lens header", self.vcm_lense_header
				for item in self.vcm_lense_header[:16]:
					hx1 = data[1][_i - 2:_i]
					_i += 2
					hx2 = data[1][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.vcm_lense_result[item] = value
				_i = 2
				for item in self.vcm_lense_header[16:]:
					hx1 = data[3][_i - 2:_i]
					_i += 2
					hx2 = data[3][_i - 2:_i]
					_i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.vcm_lense_result[item] = value
				self.vcm_lense_error_cycle = 0
				return self.vcm_lense_result
			else:
				print "wrong VCM_lense data {}".format(item)
				if self.vcm_lense_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				else:
					self.vcm_lense_error_cycle = 0
				return {}

	def read_battery_capcaity(self):
		cmd = 'adb -s {} shell "cat ./sys/class/power_supply/battery/capacity"'.format(self.adb_device_id)
		level = self.send_command(cmd)
		if str(level).isdigit():
			if int(level) < 11:
				print "Battery charge level is critical:  " + level.rstrip() + "%"
				return int(level)
		else:
			return "--"

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

	def read_B4_tepmerature(self):
		cmd = 'adb -s {} shell "./data/lcc -C -m 0 -s 0 -r -p 01 00 1c 02"'.format(self.adb_device_id)
		read_temp = self.send_command(cmd)
		return str(self.convert_IEEE754_to_float(read_temp))

	@staticmethod
	def convert_hex_to_dec(hx_data):
		hex_group = "0123456789abcdef"
		for _i in hx_data:
			if not _i.lower() in hex_group:
				print "not hex value"
				return 10000000  # if unable to convert, return unreal number
		try:
			dec_val = int(hx_data, 16)
		except SyntaxError as err:
			dec_val = 10000000
			print "Unable to perform conversion {}, adding 1000000 instead".format(err)
		return dec_val

	@staticmethod
	def convert_IEEE754_to_float(hex_string):
		new_str = ""
		for item in hex_string.split(" ")[::-1]:
			new_str = new_str + item
		try:
			float_val = round(struct.unpack('!f', new_str.decode("hex"))[0])
		except:
			return "--"
		return float_val

	def record_data_header(self):
		self.file_ref = open(
			(self.adb_device_id + "_actuator_log.csv"), "a+")
		self.file_ref.write(self.all_header)
		self.file_ref.close()

	def record_data(self, data):
		#  print "data", data
		if len(data) > 0:
			temp_row = ""
			for item in self.delta_header.split(","):
				hs_1_key = item + "_1"  # generating keys with hs1 and hs2 values
				hs_2_key = item + "_2"
				if str(data[hs_1_key]).isdigit() and str(data[hs_2_key]).isdigit():
					temp_row = temp_row + str(data[hs_2_key]-data[hs_1_key]) + ","
				else:
					temp_row = temp_row + "----" + ","
			#  print "temp row", temp_row
			self.test_data[self.cycle_count] = temp_row + str(self.read_B4_tepmerature())
			try:
				self.file_ref = open((self.adb_device_id + "_actuator_log.csv"), "a+")
				self.file_ref.write(
					str(self.cycle_count) + "," + curr_time() + "," + temp_row
					+ self.read_B4_tepmerature() + "\n")
			except IOError as err:
				print "File is not accessible {}".format(err)
			self.file_ref.close()

	def reset(self):
		self.stop = False
		self.is_runing = False

	def plot_vcm(self):
		sampling_rate = 1
		v__a1 = []
		v__a2 = []
		v__a3 = []
		v__a4 = []
		v__a5 = []
		b4__temp = []
		x_labels = []

		for cycles in sorted(self.test_data.keys()):
			if cycles % sampling_rate == 0:
				x_labels.append(cycles)
				v__a1.append((self.test_data[cycles]).split(",")[0])
				v__a2.append((self.test_data[cycles]).split(",")[1])
				v__a3.append((self.test_data[cycles]).split(",")[2])
				v__a4.append((self.test_data[cycles]).split(",")[3])
				v__a5.append((self.test_data[cycles]).split(",")[4])
				b4__temp.append((self.test_data[cycles]).split(",")[24])

		# print "a1", v__a1, "a2", v__a2, "a3", v__a3, "a5", v__a5, "B4_Temp", b4__temp

		fig = plt.figure()
		fig.canvas.set_window_title('VCM CYCLING CHART')
		host = fig.add_subplot(111)
		ax2 = host.twinx()
		host.set_ylim(0, 60000)
		ax2.set_ylim(-10, 80)
		host.set_xlabel("Cycles")
		host.set_ylabel("VCM delta")
		ax2.set_ylabel("Temperature")

		p1, = host.plot(x_labels, v__a1, color="yellow", label="A1")
		p2, = host.plot(x_labels, v__a2, color="green", label="A2")
		p3, = host.plot(x_labels, v__a3, color="blue", label="A3")
		p4, = host.plot(x_labels, v__a4, color="lavender", label="A4")
		p5, = host.plot(x_labels, v__a5, color="cyan", label="A-5")
		p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

		legends = [p1, p2, p3, p4, p5, p21]
		host.legend(handles=legends, loc='best')

		show()

	def plot_mirrors(self):
		sampling_rate = 1
		m__b1 = []
		m__b2 = []
		m__b3 = []
		m__b5 = []
		m__c1 = []
		m__c2 = []
		m__c3 = []
		m__c4 = []
		b4__temp = []
		x_labels = []

		for cycles in sorted(self.test_data.keys()):
			if cycles % sampling_rate == 0:
					x_labels.append(cycles)
					m__b1.append((self.test_data[cycles]).split(",")[5])
					m__b2.append((self.test_data[cycles]).split(",")[6])
					m__b3.append((self.test_data[cycles]).split(",")[7])
					m__b5.append((self.test_data[cycles]).split(",")[8])
					m__c1.append((self.test_data[cycles]).split(",")[9])
					m__c2.append((self.test_data[cycles]).split(",")[10])
					m__c3.append((self.test_data[cycles]).split(",")[11])
					m__c4.append((self.test_data[cycles]).split(",")[12])
					b4__temp.append((self.test_data[cycles]).split(",")[24])

		#  print "b1", m__b1, "b2", m__b2, "b3", m__b3, "b5", m__b5, "M_C1", m__c1,
		#  "M_C2", m__c2, "M_C3", m__c3, "M_C4", m__c4, "B4_Temp", b4__temp

		fig = plt.figure()
		fig.canvas.set_window_title('MIRROR CYCLING CHART')
		host = fig.add_subplot(111)
		ax2 = host.twinx()
		host.set_ylim(0, 800)
		ax2.set_ylim(-10, 80)
		host.set_xlabel("Cycles")
		host.set_ylabel("Mirror delta")
		ax2.set_ylabel("Temperature")

		p1, = host.plot(x_labels, m__b1, color="yellow", label="M-B1")
		p2, = host.plot(x_labels, m__b2, color="green", label="M-B2")
		p3, = host.plot(x_labels, m__b3, color="blue", label="M-B3")
		p4, = host.plot(x_labels, m__b5, color="lavender", label="M-B5")
		p5, = host.plot(x_labels, m__c1, color="cyan", label="M-C1")
		p6, = host.plot(x_labels, m__c2, color="gray", label="M-C2")
		p7, = host.plot(x_labels, m__c3, color="pink", label="M-C3")
		p8, = host.plot(x_labels, m__c4, color="orange", label="M-C4")
		p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

		legends = [p1, p2, p3, p4, p5, p6, p7, p8, p21]
		host.legend(handles=legends, loc='best')

		show()

	def plot_lenses(self):
		sampling_rate = 1
		l__b1 = []
		l__b2 = []
		l__b3 = []
		l__b4 = []
		l__b5 = []
		l__c1 = []
		l__c2 = []
		l__c3 = []
		l__c4 = []
		l__c5 = []
		l__c6 = []
		b4__temp = []
		x_labels = []

		for cycles in sorted(self.test_data.keys()):
			if cycles % sampling_rate == 0:
				x_labels.append(cycles)
				l__b1.append((self.test_data[cycles]).split(",")[13])
				l__b2.append((self.test_data[cycles]).split(",")[14])
				l__b3.append((self.test_data[cycles]).split(",")[15])
				l__b4.append((self.test_data[cycles]).split(",")[16])
				l__b5.append((self.test_data[cycles]).split(",")[17])
				l__c1.append((self.test_data[cycles]).split(",")[18])
				l__c2.append((self.test_data[cycles]).split(",")[19])
				l__c3.append((self.test_data[cycles]).split(",")[20])
				l__c4.append((self.test_data[cycles]).split(",")[21])
				l__c5.append((self.test_data[cycles]).split(",")[22])
				l__c6.append((self.test_data[cycles]).split(",")[23])
				b4__temp.append((self.test_data[cycles]).split(",")[24])

		#  print "L b1", l__b1, "l b2", l__b2, "l-b3", l__b3, "l-b5", l__b5, "l_C1", l__c1, \
		# "l_C2", l__c2, "l_C3", l__c3, "l_C4", l__c4, "B4_Temp", b4__temp

		fig = plt.figure()
		fig.canvas.set_window_title('LENS CYCLING CHART')
		host = fig.add_subplot(111)

		ax2 = host.twinx()
		host.set_ylim(0, 2500)
		ax2.set_ylim(-10, 80)

		host.set_xlabel("Cycles")
		host.set_ylabel("Lens delta")
		ax2.set_ylabel("Temperature")

		p1, = host.plot(x_labels, l__b1, color="yellow", label="L-B1")
		p2, = host.plot(x_labels, l__b2, color="green", label="L-B2")
		p3, = host.plot(x_labels, l__b3, color="blue", label="L-B3")
		p4, = host.plot(x_labels, l__b4, color="tan", label="L-B4")
		p5, = host.plot(x_labels, l__b5, color="lavender", label="L-B5")
		p6, = host.plot(x_labels, l__c1, color="cyan", label="L-C1")
		p7, = host.plot(x_labels, l__c2, color="gray", label="L-C2")
		p8, = host.plot(x_labels, l__c3, color="pink", label="L-C3")
		p9, = host.plot(x_labels, l__c4, color="orange", label="L-C4")
		p10, = host.plot(x_labels, l__c5, color="purple", label="L-C5")
		p11, = host.plot(x_labels, l__c6, color="gold", label="L-C6")
		p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

		legends = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p21]
		host.legend(handles=legends, loc="best")

		show()

	def run_test(self):
		data_vcm = {}  # initiating 1 len empty dictianry for further data validation
		data_lens = {}
		data_mirr = {}
		data_vcm_lens = {}
		tmp_data_1 = ""  # To temprorary store data, verify then save
		tmp_data_2 = ""
		self.read_inputs()
		print "{} device is selected \n".format(self.adb_device_id)
		self.raw_log_file_ref = open("{}_raw_data.csv".format(self.adb_device_id), "a+")
		self.raw_log_file_ref.write("N cycles,,VCM data,,,,lens data,,,,mirror data \n")
		self.raw_log_file_ref.close()
		self.record_data_header()
		st_time = time.time()
		self.asic_reset()
		# self.move_lenses()
		# self.move_mirrors()
		while not self.stop:
			self.is_runing = True
			self.cycle_count += 1
			self.is_runing = True
			self.read_B4_tepmerature()
			time.sleep(0.2)
			# counting error cycles to stop the test
			if self.mirror_error_cycles != 0 and self.lens_current_cycle != 0 and (
								self.cycle_count - self.mirror_error_cycles > 10
						or self.cycle_count - self.lens_current_cycle > 10):
					print "Test has stopped due to 10 consecutive wrong data"
					self.stop = True
			try:
				self.raw_log_file_ref = open("{}_raw_data.csv".format(self.adb_device_id), "a+")

			except IOError as err:
				print "File is not accessible {}".format(err)
			time.sleep(0.2)

			if self.run_VCM == 1 and self.run_L == 0 and self.run_M == 0:
				raw_vcm_data = self.multi_module_move(self.mode_select_VCM)
				tmp_data_1 = self.calculate_positions(raw_vcm_data, self.mode_select_VCM)
				if len(tmp_data_1) == 10:
					data_vcm = tmp_data_1
				else:
					print "VCM data valiadation Failed", tmp_data_1
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + "," + str(raw_vcm_data) + "\n"))

			elif self.run_L == 1 and self.run_VCM == 0 and self.run_M == 0:
				raw_lens_data = self.multi_module_move(self.mode_select_lens)
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + ",,,,," + str(raw_lens_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_lens_data, self.mode_select_lens)
				if len(tmp_data_1) == 22:
					data_lens = tmp_data_1
				else:
					print "Lens data validation Failed", tmp_data_1

			elif self.run_M == 1 and self.run_VCM == 0 and self.run_L == 0:
				raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + ",,,,,,,,," + str(raw_mirr_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
				if len(tmp_data_1) == 16:
					data_mirr = tmp_data_1
				else:
					print "Mirror data validation is Failed", tmp_data_1

			elif self.run_VCM == 1 and self.run_L == 1 and self.run_M == 0:
				print "running VCM and lens"
				raw_vcm_lense_data = self.multi_module_move(self.mode_select_VCM_lens)
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + "," + str(raw_vcm_lense_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_vcm_lense_data, self.mode_select_VCM_lens)
				if len(tmp_data_1) == 32:
					data_vcm_lens = tmp_data_1
				else:
					print "vcm and lens data validation Failed", tmp_data_1

			elif self.run_VCM == 1 and self.run_M == 1 and  self.run_L == 0:
				raw_vcm_data = self.multi_module_move(self.mode_select_VCM)
				raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + "," + str(raw_vcm_data) + ",,,,," + str(raw_mirr_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_vcm_data, self.mode_select_VCM)
				tmp_data_2 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
				if len(tmp_data_1) == 10 and len(tmp_data_2) == 16:
					data_vcm = tmp_data_1
					data_mirr = tmp_data_2
				else:
					print "VCM and mirr data verification failed", len(data_vcm), len(data_mirr)

			elif self.run_L == 1 and self.run_M == 1 and self.run_VCM == 0:
				raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
				raw_lens_data = self.multi_module_move(self.mode_select_lens)
				print "raw mirr", raw_mirr_data, "raw lens", raw_lens_data
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + ",,,,," + str(raw_mirr_data) + "," + str(raw_lens_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
				tmp_data_2 = self.calculate_positions(raw_lens_data, self.mode_select_lens)
				if len(tmp_data_1) == 16 and len(tmp_data_2) == 22:
					data_mirr = tmp_data_1
					data_lens = tmp_data_2
				else:
					print "M and L data validation failed", tmp_data_1, tmp_data_2

			elif self.run_VCM ==1 and self.run_M ==1 and self.run_L == 1:
				raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
				raw_vcm_lense_data = self.multi_module_move(self.mode_select_VCM_lens)
				self.raw_log_file_ref.write(
					(str(self.cycle_count) + "," + str(raw_vcm_lense_data) + ",,,,," + str(raw_mirr_data) + "\n"))
				tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
				tmp_data_2 = self.calculate_positions(raw_vcm_lense_data, self.mode_select_VCM_lens)
				if len(tmp_data_1) == 16 and len(tmp_data_2) == 32:
					data_mirr = tmp_data_1
					data_vcm_lens = tmp_data_2
				else:
					print " ALL run data validation failed", tmp_data_1, tmp_data_2
			time.sleep(0.2)

			if self.run_VCM + self.run_L == 2 or self.run_VCM + self.run_L + self.run_M == 3:
				all_data = dict(data_vcm_lens.items() + data_mirr.items())
			else:
				all_data = dict(data_lens.items() + data_mirr.items() + data_vcm.items())
			self.record_data(all_data)
			self.file_ref.close()

			if self.cycle_count % 10 == 0:
				print "%d cycles are done" % self.cycle_count
				print "%d minutes are passed" % ((time.time() - st_time) / 60)
				self.asic_reset()
				time.sleep(0.3)
			if str(self.read_battery_capcaity()).isdigit() and self.read_battery_capcaity() < 10:
				if not self.file_ref.closed:
					self.file_ref.close()
				print "Test is stop due critical battery, file saved"
			if str(self.read_battery_capcaity()).isdigit() and self.read_battery_capcaity() < 10:
				while self.read_battery_capcaity() < 95:
					self.do_charge(True)
					time.sleep(300)
			self.file_ref.close()
		else:
			cmd = ""
			self.send_command(cmd)
			if not self.raw_log_file_ref.closed:
				self.raw_log_file_ref.close()
			if not self.file_ref.closed:
				self.file_ref.close()
			cmd = 'adb -s {} shell "exit"'.format(self.adb_device_id)
			self.stop = True
			self.send_command(cmd)
		self.is_runing = False


class GUI:
	def __init__(self, master):
		self.test_module = CycleTest()
		master.title("L16 actuator cycling test")
		master.geometry("600x280")
		master.resizable(False, False)
		master.grid_rowconfigure(0, weight=1)
		master.grid_rowconfigure(1, weight=1)
		master.grid_columnconfigure(0, weight=1)
		mainframe = Frame(master, width=500, height=200, bg="PeachPuff3")
		mainframe.grid(sticky=(N, W, E, S))
		self.tkvar = StringVar(mainframe)
		choices = self.test_module.get_dev_list()
		self.VCM_select_var = IntVar()
		self.VCM_select_var.set(1)
		self.L_select_var = IntVar()
		self.L_select_var.set(1)
		self.M_select_var = IntVar()
		self.M_select_var.set(1)
		self.messages = ["Stopped", "Selected-", "Please connect!!!", "Stop cycle first!", "No device", "Running"]

		if len(choices) > 0:
			self.tkvar.set(choices[0])  # set the default option
		else:
			print "No connected devices"
			exit()

		#  Drop down menu
		popupmenu = OptionMenu(mainframe, self.tkvar, *choices)
		popupmenu.grid(row=0, column=5)
		self.pop_up_lbl = Label(mainframe, text="Choose the unit ")
		self.pop_up_lbl.grid(row=0, column=4)

		#  Configure layout
		for i in range(6):
			mainframe.columnconfigure(i, weight=3, minsize=60)
		for i_1 in range(13):
			mainframe.rowconfigure(i_1, weight=1, minsize=45)

		#  Buttons function list
		func_list = (
			self.connect, self.stop, self.show_vcm_graph, self.show_mirror_graph, self.show_lens_graph,
			self.run_test, self.open_logs)

		butt_name_list = ["Connect", "Stop", "VCM graph", "Mirror graph", "Lens graph", "Run Test", "Open logs"]

		i = 0
		for i_column in range(2):
			for i_row in range(1, 6):
					if i_column == 1 and 2 < i_row < 6:  # Avoid put button on 2 column row 1,2
						continue
					bt = Button(mainframe, text=butt_name_list[i], command=func_list[i])
					bt.configure(height=2, width=12)
					bt.grid(column=i_column, row=i_row, sticky=W)
					if i < 6:
						i += 1

		but_exit = Button(mainframe, text="Exit", command=self.exit)
		but_exit.configure(height=2, width=10)
		but_exit.grid(column=5, row=5)

		status_lbl = Label(mainframe, text="Test status")
		status_lbl.grid(row=1, column=3)

		self.run_status = Label(mainframe, text="Not Run")
		self.run_status.grid(row=2, column=3)

		self.live_status_lbl = Label(mainframe, text="        ")
		self.live_status_lbl.grid(row=3, column=3)

		mod_a_check_but = Checkbutton(mainframe, text="VCM", var=self.VCM_select_var)
		mod_a_check_but.grid(row=3, column=1)

		mod_l_check_but = Checkbutton(mainframe, text="Lens", var=self.L_select_var)
		mod_l_check_but.grid(row=5, column=1)

		mod_m_check_but = Checkbutton(mainframe, text="Mirror", var=self.M_select_var)
		mod_m_check_but.grid(row=4, column=1)

	def connect(self):
		print "connected"
		self.test_module.connect()
		self.test_module.copy_lcc()
		self.test_module.copy_prog_app()

	def pause(self):
		pass

	def show_vcm_graph(self):
		self.test_module.plot_vcm()

	def show_mirror_graph(self):
		self.test_module.plot_mirrors()

	def show_lens_graph(self):
		self.test_module.plot_lenses()

	def stop(self):
		self.test_module.stop = True
		time.sleep(.5)
		self.run_status.config(text="Stopped")

	@staticmethod
	def open_logs():
		import os
		curr_loc = os.getcwd()
		subprocess.Popen(r'explorer /select, {}'.format(curr_loc))

	def exit(self):
		self.test_module.stop = True
		time.sleep(1)
		sys.exit()

	def run_test(self):
		if self.test_module.adb_device_id is not None:
			if not self.test_module.is_runing:
				self.test_module.reset()
				tr = Thread(target=self.test_module.run_test)
				tr.start()

	def update_ui(self):
		self.pop_up_lbl.after(100, self.update_ui)
		if self.test_module.adb_device_id is None:
			self.run_status.config(text=self.messages[2])
			self.live_status_lbl.config(text=self.messages[4])
		else:
			self.run_status.config(text=self.messages[1] + str(self.test_module.adb_device_id[-3:]))
		if self.test_module.is_runing:
			self.live_status_lbl.config(text="{} cycles are done".format(self.test_module.cycle_count))
			self.run_status.config(text=self.messages[5])
		elif not self.test_module.is_runing:
			self.live_status_lbl.config(text=self.messages[0])



if debug:
	dut = CycleTest()
	dut.adb_device_id = "LFCLHD4781000209"
	# dut.move_lenses()
	# dut.move_vcm()
	# dut.run_test()
	for i in range(4):
		print dut.multi_module_move(4)


else:
	main_window = Tk()
	start_test_gui = GUI(main_window)
	main_window.after(1, start_test_gui.update_ui())
	main_window.mainloop()
