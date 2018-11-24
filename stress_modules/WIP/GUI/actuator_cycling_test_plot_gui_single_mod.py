#################################################
# Ligh L16 stress module test                   #
# current version V0.12                         #
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
# #  d A module move and position read          #
# # add A module move and position read         #
# V 0.10                                        #
# # selective run for each type of actuator     #
# # log output ajduted acording run type        #
# # change run mode on the fly, without reopen  #
# # fixed bug related A and lens run calculation#
# # simplified code, removed separate functions #
# # add A module move and position read         #
# # reset test data before each run             #
# #  more UI control and status update          #
# # data validation before creating chart       #
# # More status update messages                 #
# # Battery indication on UI                    #
#  V 0.11                                       #
# # redesigned connect button                   #
# #    it support 3 action                      #
# # app will open other instance for diff device#
# # dev ids on graphs                           #
# # V 0.12                                      #
# added temperature data validatio              #
#################################################
# TODO add start  time on UI
# TODO open/close plots by same button

import subprocess
import time
from datetime import datetime
from time import strftime, localtime
import struct
from threading import Thread
from Tkinter import *
#import tkinter
from Tkinter import *
import matplotlib.pyplot as plt
import os
from sys import stdout

#debug = True
debug = False


def curr_time():
	return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class CycleTest:
	def __init__(self):
		current_version = "0.12"
		print "Module test program, version %s" % current_version
		self.file_name = '\\actuator_cycling_test_plot.py'
		self.curr_path = os.getcwd()
		# LCC command components
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
		self.mode_select_lens
		self.hs1 = 1
		self.hs2 = 2
		self.stop = False
		self.is_runing = False
		self.is_paused = False
		self.dev_list = []
		self.adb_device_id = None
		self.cycle_count = 0
		self.all_mirr_data = None
		self.bat_capacity = None
		self.mir_result = {}
		self.lens_result = {}
		self.vcm_result = {}
		self.vcm_lense_result = {}
		self.mod_data_range_possit = []  # plotting [VCM -5, lense-11, mirror-8, temp_sens-6]
		self.file_ref = None
		self.all_lens_data = None
		self.all_mirr_data = None
		self.charging_status = None
		self.raw_log_file_ref = None
		self.lens_error_cycles = 0
		self.mirror_error_cycles = 0
		self.vcm_error_cycle = 0
		self.vcm_lense_error_cycle = 0
		self.lens_delta_header = [
			'L_B1', 'L_B2', 'L_B3', 'L_B4', 'L_B5', 'L_C1', 'L_C2', 'L_C3', 'L_C4', 'L_C5', 'L_C6']
		self.mirror_delta_header = [
			'M_B1', 'M_B2', 'M_B3', 'M_B5', 'M_C1', 'M_C2', 'M_C3', 'M_C4']
		self.vcm_delta_header = ['A1', 'A2', 'A3', 'A4', 'A5']
		# test run modes
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

		self.vcm_header = ['A5', 'A4', 'A3','A2', 'A1']
		self.vcm_header_hs1 = []
		self.vcm_header_hs2 = []

		# self.vcm_header_hs1 = ['A1_1', 'A2_1', 'A3_1', 'A4_1', 'A5_1']
		# self.vcm_header_hs2 = ['A1_2', 'A2_2', 'A3_2', 'A4_2', 'A5_2']

		self.b_mod = ['B5', 'B4', 'B3', 'B2', 'B1']
		self.b_mod_hs1 = []
		self.b_mod_hs2 = []
		# self.b_mod_hs1 = ['B1_1', 'B2_1', 'B3_1', 'B4_1', 'B5_1']
		# self.b_mod_hs2 = ['B1_2', 'B2_2', 'B3_2', 'B4_2', 'B5_2']

		self.c_mod = ['C6', 'C5', 'C4', 'C3', 'C2', 'C1']
		self.c_mod_hs1 = []
		self.c_mod_hs2 = []
		# self.c_mod_hs1 = ['C1_1', 'C2_1', 'C3_1', 'C4_1', 'C5_1', 'C6_1']
		# self.c_mod_hs2 = ['C1_2', 'C2_2', 'C3_2', 'C4_2', 'C5_2', 'C6_2']

		self.all_vcm_header = self.vcm_header_hs1 + self.vcm_header_hs2
		self.all_lens_header = lens_list_hs1 + lens_list_hs2
		self.all_mirr_header = mirr_list_hs1 + mirr_list_hs2
		#  When run VCM and lense, VCM calculation is negative, hense hs2 first then hs1
		self.vcm_lense_header = self.vcm_header_hs2 + lens_list_hs1 + self.vcm_header_hs1 + lens_list_hs2
		self.test_data = {}
		self.is_runing = False
		self.delta_header = None
		self.all_header = None
		self.mode_state = []  # variable to store last run state, for rerun purpose
		self.data = {}  # setting frokm gui

	def get_dev_list(self):
		raw_devs = self.send_command("adb devices")
		self.dev_list = re.findall("LFC\S+", raw_devs)
		if len(self.dev_list) > 0:
			return self.dev_list

	def get_button_state(self):
		self.data = start_test_gui.get_button_status()


	def convert_module_set_to_bits(self):
		"""
		:return: b_01, b_02, b_03 00111110 00000000 00000000
		"""
		print "convert module set to abit"
		self.bitmask_01 = "0" # besides G global bitmask
		self.bitmask_02 = ""
		self.bitmask_03 = "0000000"  # only C6
		data_list = self.data.keys()
		data_list.sort()
		for item in data_list:
			if "Mirror" not in item.lower() or "Lens" not in item.lower() or "VCM" not in item.lower():
				if len(self.bitmask_01) < 8:
					self.bitmask_01 = str(self.data[item]) + self.bitmask_01
					continue
				if len(self.bitmask_02) < 8:
					self.bitmask_02 = str(self.data[item]) + self.bitmask_02
					continue
				if len(self.bitmask_03) < 8:
					self.bitmask_03 = self.bitmask_03 + str(self.data[item])
		#print "bitmasl", self.bitmask_01
		print "bit1", self.bitmask_01, "bit2", self.bitmask_02, "bit3", self.bitmask_03
		return self.bitmask_01, self.bitmask_02, self.bitmask_03

	def count_active_modules(self, b_01, b_02, b_03):
		active_a_accts = b_01[2:8].count("1")
		active_b_accts = b_01[:2].count("1") + b_02[5:].count("1")
		active_c_accts = b_02[:5].count("1") + b_03[7:].count("1")
		active_module_counts = active_a_accts + active_b_accts + active_c_accts
		print "counting active modules for run command", active_module_counts
		return active_module_counts

	def overwrite_bitmasks(self, b_01, b_02, b_03, mode):
		print "received data to overwrite", b_01, b_02, b_03
		# mode overwrite in mode VCM and Mirror, lens
		if mode == 1:
			b_01 = "00" + b_01[2:]  # Overriding bitmask to avoid lens move
			b_02 = "00000000"
			b_03 = "00000000"
		elif mode == 2: # lens
			b_01 = b_01[:2] + "000000"  # Overriding bitmask to avoid VCM move

		elif mode == 3:  # mirror removeing non moving mirror
			print "doing mirror bit overwrite"
			b_01 = b_01[:2] + "000000"
			b_02 = "0" + b_02[1:6] + "0" + b_02[7]
			b_03 = "00000000"
		print "overwriting func", b_01, b_02, b_03

		return b_01, b_02, b_03


	def generate_data_headers(self):
		# print "config data herader"
		# print self.bitmask_01, self.bitmask_02, self.bitmask_03
		in_pos = 0
		# A VCM
		for i in self.bitmask_01[2:8]:
			if i == "1":
				self.vcm_header_hs1.append(self.vcm_header[in_pos] + "_1")
				self.vcm_header_hs2.append(self.vcm_header[in_pos] + "_2")
				self.vcm_header_hs1.sort()
				self.vcm_header_hs2.sort()
			in_pos += 1

		in_pos = 0
		# B modules
		for i in self.bitmask_02[5:]+ self.bitmask_01[:2]:
			if i == "1":
				self.b_mod_hs1.append(self.b_mod[in_pos] + "_1")
				self.b_mod_hs2.append(self.b_mod[in_pos] + "_2")
				self.b_mod_hs1.sort()
				self.b_mod_hs2.sort()
			in_pos += 1

		in_pos = 0
		# C modules
		for i in self.bitmask_03[7] + self.bitmask_02[:5]:
			if i == "1":
				self.c_mod_hs1.append(self.c_mod[in_pos] + "_1")
				self.c_mod_hs2.append(self.c_mod[in_pos] + "_2")
				self.c_mod_hs1.sort()
				self.c_mod_hs2.sort()
			in_pos += 1
		print "vcm hs1", self.vcm_header_hs1, "vcm hs2", self.vcm_header_hs2, "b _hs1", self.b_mod_hs1, "b_hs2", \
			self.b_mod_hs2,	"C_hs_1", self.c_mod_hs1, "c_hs2", self.c_mod_hs2

		return self.vcm_header_hs1 + self.b_mod_hs1 + self.c_mod_hs1, \
			self.vcm_header_hs2 + self.b_mod_hs2 + self.c_mod_hs2

	def generate_mode(self):
		pass

	def convert_to_hex_group(self, b_01, b_02, b_03):
		#all_bin_data = self.convert_module_set_to_bits()
		byte_1 = hex(int(b_01, 2))
		byte_2 = hex(int(b_02, 2))
		byte_3 = hex(int(b_03, 2))
		byte_1 = (byte_1[2:]).upper()
		byte_2 = byte_2[2:].upper()
		byte_3 = byte_3[2:].upper()
		if len(byte_1) != 2:
			byte_1 = "0" + byte_1
		if len(byte_2) != 2:
			byte_2 = "0" + byte_2
		if len(byte_3) != 2:
			byte_3 = "0" + byte_3
		sub_command = " " + byte_1 + " " + byte_2 + " " + byte_3
		print "bytes", byte_1, byte_2, byte_3
		return sub_command


	def connect(self):
		self.get_button_state()
		"""
		1. verify pluged in android devices
		2. let user  to choose which device will be used
		3. run other copy of program if different dev is choosed
		4. eliminate connection to the same unit twice
		:return: device ID
		"""

		if self.adb_device_id is None:
			self.adb_device_id = start_test_gui.tkvar.get()
		elif self.adb_device_id != start_test_gui.tkvar.get():
			full_path = '{}'.format(self.curr_path) + self.file_name
			with open(os.devnull, 'r+b', 0) as DEVNULL:
				p = subprocess.Popen(
					['Python', full_path], stdin=DEVNULL, stdout=DEVNULL, stderr=stdout)
			if p.poll():  # the process already finished and it has nonzero exit code
				sys.exit(p.returncode)
		else:
			if self.is_runing:
				self.stop = True

		return self.adb_device_id


	def read_inputs(self):
		self.run_VCM = self.data["VCM"]
		self.run_L = self.data["Lens"]
		self.run_M = self.data["Mirror"]
		if self.run_VCM == 1 and self.run_M == 0 and self.run_L == 0:
			self.delta_header = ",".join(self.vcm_delta_header)
			self.mod_data_range_possit = [4, 0, 0, 5]
		elif self.run_L == 1 and self.run_VCM == 0 and self.run_M == 0:
			self.delta_header = ",".join(self.lens_delta_header)
			self.mod_data_range_possit = [0, 10, 0, 11]
		elif self.run_M == 1 and self.run_VCM == 0 and self.run_L == 0:
			self.delta_header = ",".join(self.mirror_delta_header)
			self.mod_data_range_possit = [0, 0, 7, 8]
		elif self.run_VCM == 1 and self.run_L == 1 and self.run_M == 0:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.lens_delta_header)
			self.mod_data_range_possit = [4, 15, 0, 16]
		elif self.run_VCM == 1 and self.run_M == 1 and self.run_L == 0:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.mirror_delta_header)
			self.mod_data_range_possit = [4, 0, 12, 13]
		elif self.run_L == 1 and self.run_M == 1 and self.run_VCM == 0:
			self.delta_header = ",".join(self.lens_delta_header) + "," + ",".join(self.mirror_delta_header)
			self.mod_data_range_possit = [0, 10, 18, 19]
		elif self.run_VCM + self.run_L + self.run_M == 3:
			self.delta_header = ",".join(self.vcm_delta_header) + "," + ",".join(self.lens_delta_header) + \
				"," + ",".join(self.mirror_delta_header)
			self.mod_data_range_possit = [4, 15, 23, 24]
		else:
			sys.exit("No mode selected")
		self.all_header = \
			"N_{},".format(strftime("%m-%d-%Y", localtime())) + "Time" + "," + \
			self.delta_header + "," + "B4 temp." + "\n"
		#  print "vcn state", self.run_VCM, "lense state",  self.run_L, "mirr state", self.run_M
		print "Connected"
		return self.run_VCM, self.run_L, self.run_M

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
		cmd = 'adb -s {} shell /data/prog_app_p2 -q'.format(self.adb_device_id)
		self.send_command(cmd)

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

	def order_active_module_bits(self):
		"""
		reverse bits to alphabetical irder ob modules
		leave only active bits for possition calculation
		:return:
		"""
		b_01_a1_b2 = self.bitmask_01[::-1]
		b_02_b3_c5 = self.bitmask_02[::-1]
		b_03_c6 = self.bitmask_03[::-1]
		active_bit_sequence = b_01_a1_b2.translate(None, "0") + b_02_b3_c5.translate(None, "0") + \
			b_03_c6.translate(None, "0")
		return active_bit_sequence


	def multi_module_move(self, mode):
		all_pos = []
		VCM_pos_data_1, VCM_pos_data_2, M_pos_data_1, M_pos_data_2 = (None, None, None, None)
		"""
		:param mode: 1-VCM, 2-Lens, 3- Mirror, 4-VCM and lens
		:return: hs1+hs2 pos list
		"""
		#self.convert_module_set_to_bits()

		if self.data["Mirror"]:  # mirror move and A modules  move if specified in command

			print "Mirror", mode
			b_01, b_02, b_03 = self.overwrite_bitmasks(self.bitmask_01, self.bitmask_02, self.bitmask_03, 3)
			# print "b_01, b_02, b_03", b_01, b_02, b_03

			sub_command = self.convert_to_hex_group(b_01, b_02, b_03)
			print "sub command", sub_command
			active_acct_count = self.count_active_modules(b_01, b_02, b_03)
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					sub_command + self.hs1_bit * active_acct_count))
			print "mirror send hs1", cmd
			self.send_command(cmd)
			time.sleep(0.2)
			M_pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_mirror, sub_command)
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + sub_command +
					self.all_mir_bitmask + self.hs2_bit * active_acct_count))
			print "mirror send hs2", cmd
			self.send_command(cmd)
			time.sleep(0.2)
			M_pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_mirror, sub_command)

		if self.data["VCM"] == 1: # VCM  move
			# if self.data["Lens"] == 1 or self.data["Mirror"] == 1:
			# overwrite to eliminate VCM and lense move same time
			b_01, b_02, b_03 = self.overwrite_bitmasks(self.bitmask_01, self.bitmask_02, self.bitmask_03, 1)
			print "b_01, b_02, b_03", b_01, b_02, b_03
			sub_command = self.convert_to_hex_group(b_01, b_02, b_03)
			print "sub command", sub_command
			active_acct_count = self.count_active_modules(b_01, b_02, b_03)

			print "VCM", mode, "active count" , active_acct_count

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (self.channel_sel_write + self.tran_id +
				self.A_mod_move_com_id + sub_command + self.hs2_bit * active_acct_count))
			self.send_command(cmd)
			time.sleep(0.2)
			print "VCM send hs1", cmd
			VCM_pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_VCM, sub_command)

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (self.channel_sel_write + self.tran_id +
				                     self.A_mod_move_com_id + sub_command + self.hs1_bit * active_acct_count))
			print "VCM send hs2", cmd
			self.send_command(cmd)
			time.sleep(0.2)
			VCM_pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_VCM, sub_command)
			print "mode 1 , pos data", VCM_pos_data_1, VCM_pos_data_2

		elif False:  # VCM and lens move
			print "mode 4 ", mode
			b_01, b_02, b_03 = self.overwrite_bitmasks(self.bitmask_01, self.bitmask_02, self.bitmask_03, mode)
			print "b_01, b_02, b_03", b_01, b_02, b_03
			sub_command = self.convert_to_hex_group(b_01, b_02, b_03)
			print "sub command", sub_command
			active_acct_count = self.count_active_modules(b_01, b_02, b_03)

			cmd='adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (self.channel_sel_write + self.tran_id +
				self.A_mod_move_com_id + sub_command + self.hs2_bit * active_acct_count))
			self.send_command(cmd)
			time.sleep(0.2)

			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_VCM_lens)
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + actuator_move_command + self.hs2_bit * active_acct_count)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_VCM_lens)
			all_pos = pos_data_1 + pos_data_2

		elif False: # self.data["Lens"] == 1:  # lens only move
			print "Lense", mode
			b_01, b_02, b_03 = self.overwrite_bitmasks(self.bitmask_01, self.bitmask_02, self.bitmask_03, mode)
			print "b_01, b_02, b_03", b_01, b_02, b_03
			sub_command = self.convert_to_hex_group(b_01, b_02, b_03)
			print "sub command", sub_command
			active_acct_count = self.count_active_modules(b_01, b_02, b_03)

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + sub_command + self.hs1_bit * active_acct_count)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_lens, sub_command)

			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.lens_move_com_id + sub_command + self.hs2_bit * active_acct_count)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_lens, sub_command)


		# all_pos = VCM_pos_data_1.insert(0, "VCM") + VCM_pos_data_2.insert(0, "VCM") + M_pos_data_1.insert(0, "M") +\
		#           M_pos_data_2.isert(0, "M")

		print "all poss", VCM_pos_data_1, VCM_pos_data_2, M_pos_data_1, M_pos_data_2



	def multi_module_move_orig(self, mode):
		pos_data_1 = []
		pos_data_2 = []
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
			print "pos 1 data", pos_data_1
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_write + self.tran_id +
				self.A_mod_move_com_id + self.A_mod_bitmask + self.hs1_bit * 5)
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_VCM)
			print "pos 2daTA", pos_data_2

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

		if mode == 3:  # mirror only move
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					self.all_mir_bitmask + self.hs1_bit * 8))
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_1 = self.multi_module_pos_read(self.hs1, self.mode_select_mirror)
			print "pos 1 data Mirr", pos_data_1
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_write + self.tran_id + self.mir_move_com_id +
					self.all_mir_bitmask + self.hs2_bit * 8))
			self.send_command(cmd)
			time.sleep(0.2)
			pos_data_2 = self.multi_module_pos_read(self.hs2, self.mode_select_mirror)
			print "pos 2 data Mirr", pos_data_2

		if mode == 4:  # VCM and lens move
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

	def multi_module_pos_read(self, hs, mode, actuator_move_command):

		# TODO remove duplicate function call

		cmd = ""
		if self.data["Mirror"] == 1:  # read mirror positions and VCM if specified
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
					actuator_move_command))

		elif self.data["VCM"] == 1:  # read VCM
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
				    actuator_move_command)

		elif mode == 1:  # read vcm position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.A_mod_pos_com_id +
				actuator_move_command)
		elif mode == 2:  # read lens position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
				actuator_move_command)

		print "pos read command", cmd
		position_data = self.send_command(cmd)
		if hs == 1:
			position_data = [1] + ["".join([_i.strip() for _i in position_data])]
		elif hs == 2:
			position_data = [2] + ["".join([_i.strip() for _i in position_data])]
		print "possition", position_data
		return position_data

	def multi_module_pos_read_orig(self, hs, mode):
		cmd = ""
		if mode == 1:  # read vcm position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.A_mod_pos_com_id +
				self.A_mod_bitmask)
		elif mode == 2:  # read lens position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
				self.all_lens_bitmask)
		elif mode == 3:  # read mirror positions
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
					self.all_mir_bitmask))
		elif mode == 4:  # read VCM and lens position
			cmd = 'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
				self.global_bitmask)
		position_data = self.send_command(cmd)
		if hs == 1:
			position_data = [1] + ["".join([_i.strip() for _i in position_data])]
		elif hs == 2:
			position_data = [2] + ["".join([_i.strip() for _i in position_data])]
		return position_data

	def calculate_positions(self, data, mir_len_vcm):
		#  print "data", data
		#  print "mode", mir_len_vcm
		"""
		:param data: for mirrors [
		0, "45100012000456078009800F011A0100", 1,
		45100012000456078009800F011A0100]
		for lenses [0, 22 byte data, 1, 22 byte data]
		:param mir_len_vcm: 1 mirror 2 lens
		:return: dic {L_B1_1:400', 'L_B2_1:400',..} or dic {M_B3_1:123', 'M_B4_1:322',..}
		"""
		active_bit_set_string  = self.order_active_module_bits()

		_i = 2
		item = None
		if self.data["VCM"] == 1:  # VCM
		#if mir_len_vcm == 1:  # VCM
			if len(data[1]) == self.active_a_actuator * 4 and self.active_a_actuator * 4 == 20:
				# print "all vcm header", self.all_vcm_header
				# print "data", data
				self.vcm_header_hs1.sort()
				for item in self.vcm_header_hs1:
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
				self.vcm_header_hs2.sort()
				for item in self.vcm_header_hs2:
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
				print "VCM mve result", self.vcm_result
				return self.vcm_result
			else:
				print "wrong VCM data", data[1], data[3],
				if self.vcm_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				return {}

		elif self.data["Lens"] == 1:  # lens
		#elif mir_len_vcm == 2:  # lens
			# TODO need use custom dataset for bercause module bitmas was overwritten
			if len(data[1]) == self.active_module_counts * 4 and len(data[3]) == self.active_module_counts * 4:
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
				print "wrong lens data {}", data[1], data[3]
				if self.lens_error_cycles == 0:
					self.lens_error_cycles = self.cycle_count
				return {}

		elif mir_len_vcm == 3:  # mirror
			if len(data[1]) == self.active_module_counts and len(data[3]) == self.active_module_counts:
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
				print "wrong mirror data", data[1], data[3]
				print "cycles:", self.cycle_count
				#  counting wrong data cycles, to stop the test
				if self.mirror_error_cycles == 0:
					self.mirror_error_cycles = self.cycle_count
				return {}

		elif mir_len_vcm == 4:  # VCM + Lens
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
				print "wrong VCM_lense data", data[1], data[3]
				if self.vcm_lense_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				return {}


	def calculate_positions_orig(self, data, mir_len_vcm):
		#  print "data", data
		#  print "mode", mir_len_vcm
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
			if len(data[1]) == self.active_a_actuator * 4 and self.active_a_actuator * 4 == 20:
				# print "all vcm header", self.all_vcm_header
				# print "data", data
				self.vcm_header_hs1.sort()
				for item in self.vcm_header_hs1:
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
				self.vcm_header_hs2.sort()
				for item in self.vcm_header_hs2:
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
				print "VCM mve result", self.vcm_result
				return self.vcm_result
			else:
				print "wrong VCM data", data[1], data[3],
				if self.vcm_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				return {}

		elif mir_len_vcm == 2:  # lens
			if len(data[1]) == 44  and len(data[3]) == 44:
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
				print "wrong lens data {}", data[1], data[3]
				if self.lens_error_cycles == 0:
					self.lens_error_cycles = self.cycle_count
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
				print "wrong mirror data", data[1], data[3]
				print "cycles:", self.cycle_count
				#  counting wrong data cycles, to stop the test
				if self.mirror_error_cycles == 0:
					self.mirror_error_cycles = self.cycle_count
				return {}

		elif mir_len_vcm == 4:  # VCM + Lens
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
				print "wrong VCM_lense data", data[1], data[3]
				if self.vcm_lense_error_cycle == 0:
					self.vcm_error_cycle = self.cycle_count
				return {}

	def read_battery_capcaity(self):
		cmd = 'adb -s {} shell "cat ./sys/class/power_supply/battery/capacity"'.format(self.adb_device_id)
		level = self.send_command(cmd)
		if str(level).isdigit():
			if int(level) < 11:
				if debug:
					print "Battery charge level is critical:  " + level.rstrip() + "%"
				return int(level)
			else:
				return int(level)
		else:
			return 0

	def do_charge(self, need_charge):
		tries = 3
		#  Enabling charging control...
		self.send_command('adb -s {} shell "setprop persist.fih.flight_flag 0"'.format(self.adb_device_id))
		time.sleep(0.2)
		verify_status_cmd = 'adb -s {} shell ' \
			'"cat /sys/class/power_supply/battery/charging_enabled"'.format(self.adb_device_id)
		if need_charge:
			# enable charging
			cmd = 'adb -s {} shell "echo 1 > ./sys/class/power_supply/battery/charging_enabled"' \
				.format(self.adb_device_id)
			self.send_command(cmd)
			time.sleep(1)
			self.charging_status = self.send_command(verify_status_cmd)
			while "1" not in str(self.charging_status) and tries > 0:
				print "Error to enable charging. Trying to re-enable"
				time.sleep(1)
				self.send_command(cmd)
				tries -= 1
		elif not need_charge:
			# disable charging
			cmd = 'adb -s {} shell "echo 0 > ./sys/class/power_supply/battery/charging_enabled"' \
				.format(self.adb_device_id)
			self.send_command(cmd)
			time.sleep(1)
			self.charging_status = self.send_command(verify_status_cmd)
			while "0" not in str(self.charging_status) and tries > 0:
				print "Error to disable charging. Trying to re-enable"
				time.sleep(1)
				self.send_command(cmd)
				tries -= 1

	def read_B4_temperature(self):
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
			print "Error in conversion"
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
					temp_row = temp_row + str(data[hs_2_key] - data[hs_1_key]) + ","
			b4_temprature = self.read_B4_temperature()
			if "--" not in b4_temprature:
				data_row = temp_row + str(b4_temprature)
				self.test_data[self.cycle_count] = data_row
				try:
					self.file_ref = open((self.adb_device_id + "_actuator_log.csv"), "a+")
					self.file_ref.write(
						str(self.cycle_count) + "," + curr_time() + "," + data_row + "\n")
				except IOError as err:
					print "File is not accessible {}".format(err)
				self.file_ref.close()

	def reset(self):
		self.stop = False
		self.is_runing = False

	def plot_vcm(self):
		if len(self.test_data) > 5 and self.mod_data_range_possit[0] != 0:
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
					b4__temp.append(float((self.test_data[cycles]).split(",")[self.mod_data_range_possit[3]]))

			# print "a1", v__a1, "a2", v__a2, "a3", v__a3, "a5", v__a5, "B4_Temp", b4__temp

			fig = plt.figure()
			fig.canvas.set_window_title('VCM CYCLING GRAPH ID:{}'.format(self.adb_device_id))
			host = fig.add_subplot(111)
			ax2 = host.twinx()
			host.set_ylim(0, 45000)
			ax2.set_ylim(-10, 80)
			host.set_xlabel("Cycles")
			host.set_ylabel("VCM delta")
			ax2.set_ylabel("Temperature")

			p1, = host.plot(x_labels, v__a1, color="brown", label="A1")
			p2, = host.plot(x_labels, v__a2, color="green", label="A2")
			p3, = host.plot(x_labels, v__a3, color="blue", label="A3")
			p4, = host.plot(x_labels, v__a4, color="coral", label="A4")
			p5, = host.plot(x_labels, v__a5, color="cyan", label="A-5")
			p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

			legends = [p1, p2, p3, p4, p5, p21]
			host.legend(handles=legends, loc='best')

			fig.show()
		else:
			print "No VCM data available"

	def plot_mirrors(self):
		if len(self.test_data) > 5 and self.mod_data_range_possit[2] != 0:
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
					m__b1.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 7])
					m__b2.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 6])
					m__b3.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 5])
					m__b5.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 4])
					m__c1.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 3])
					m__c2.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 2])
					m__c3.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2] - 1])
					m__c4.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[2]])
					b4__temp.append(float((self.test_data[cycles]).split(",")[self.mod_data_range_possit[3]]))

			# print "b1", m__b1, "b2", m__b2, "b3", m__b3, "b5", m__b5, "M_C1", m__c1,
			#  "M_C2", m__c2, "M_C3", m__c3, "M_C4", m__c4, "B4_Temp", b4__temp

			fig = plt.figure()
			fig.canvas.set_window_title('MIRROR CYCLING GRAPH ID:{}'.format(self.adb_device_id))
			host = fig.add_subplot(111)
			ax2 = host.twinx()
			host.set_ylim(0, 600)
			ax2.set_ylim(-10, 80)
			host.set_xlabel("Cycles")
			host.set_ylabel("Mirror delta")
			ax2.set_ylabel("Temperature")

			p1, = host.plot(x_labels, m__b1, color="brown", label="M-B1")
			p2, = host.plot(x_labels, m__b2, color="green", label="M-B2")
			p3, = host.plot(x_labels, m__b3, color="blue", label="M-B3")
			p4, = host.plot(x_labels, m__b5, color="coral", label="M-B5")
			p5, = host.plot(x_labels, m__c1, color="cyan", label="M-C1")
			p6, = host.plot(x_labels, m__c2, color="gray", label="M-C2")
			p7, = host.plot(x_labels, m__c3, color="pink", label="M-C3")
			p8, = host.plot(x_labels, m__c4, color="orange", label="M-C4")
			p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

			legends = [p1, p2, p3, p4, p5, p6, p7, p8, p21]
			host.legend(handles=legends, loc='best')
			fig.show()
		else:
			print "No mirror data available"

	def plot_lenses(self):
		if len(self.test_data) > 5 and self.mod_data_range_possit[1] != 0:
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
					l__b1.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 10])
					l__b2.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 9])
					l__b3.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 8])
					l__b4.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 7])
					l__b5.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 6])
					l__c1.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 5])
					l__c2.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 4])
					l__c3.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 3])
					l__c4.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 2])
					l__c5.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1] - 1])
					l__c6.append((self.test_data[cycles]).split(",")[self.mod_data_range_possit[1]])
					b4__temp.append(float((self.test_data[cycles]).split(",")[self.mod_data_range_possit[3]]))

			# print "L b1", l__b1, "l b2", l__b2, "l-b3", l__b3, "l-b5", l__b5, "l_C1", l__c1, \
			# "l_C2", l__c2, "l_C3", l__c3, "l_C4", l__c4, "B4_Temp", b4__temp

			fig = plt.figure()
			fig.canvas.set_window_title('LENS CYCLING GRAPH ID{}'.format(self.adb_device_id))
			host = fig.add_subplot(111)

			ax2 = host.twinx()
			host.set_ylim(0, 2500)
			ax2.set_ylim(-10, 80)

			host.set_xlabel("Cycles")
			host.set_ylabel("Lens delta")
			ax2.set_ylabel("Temperature")

			p1, = host.plot(x_labels, l__b1, color="brown", label="L-B1")
			p2, = host.plot(x_labels, l__b2, color="green", label="L-B2")
			p3, = host.plot(x_labels, l__b3, color="blue", label="L-B3")
			p4, = host.plot(x_labels, l__b4, color="tan", label="L-B4")
			p5, = host.plot(x_labels, l__b5, color="darkviolet", label="L-B5")
			p6, = host.plot(x_labels, l__c1, color="cyan", label="L-C1")
			p7, = host.plot(x_labels, l__c2, color="gray", label="L-C2")
			p8, = host.plot(x_labels, l__c3, color="pink", label="L-C3")
			p9, = host.plot(x_labels, l__c4, color="orange", label="L-C4")
			p10, = host.plot(x_labels, l__c5, color="purple", label="L-C5")
			p11, = host.plot(x_labels, l__c6, color="maroon", label="L-C6")
			p21, = ax2.plot(x_labels, b4__temp, color="red", label="Temperature")

			legends = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p21]
			host.legend(handles=legends, loc="best")

			fig.show()
		else:
			print "No lens data is available"

	def run_test(self):
		data_vcm = {}
		data_lens = {}
		data_mirr = {}
		data_vcm_lens = {}
		self.read_inputs()
		if self.mode_state != self.mod_data_range_possit:
			self.test_data = {}  # reset tes data if setting are changed, to maintain uniform data structure
			self.cycle_count = 0
		print "{} device is selected \n".format(self.adb_device_id)
		self.raw_log_file_ref = open("{}_raw_data.csv".format(self.adb_device_id), "a+")
		self.raw_log_file_ref.write("N cycles,,VCM data,,,,lens data,,,,mirror data \n")
		self.raw_log_file_ref.close()
		self.record_data_header()
		st_time = time.time()
		self.asic_reset()
		self.convert_module_set_to_bits()
		self.generate_data_headers()
		while not self.stop:
			self.is_paused = False
			self.bat_capacity = self.read_battery_capcaity()
			self.mode_state = self.mod_data_range_possit
			self.is_runing = True
			self.cycle_count += 1
			# counting error cycles to stop the test
			if self.mirror_error_cycles != 0 and self.lens_error_cycles != 0 and self.vcm_error_cycle \
				and self.vcm_lense_error_cycle and (
					self.cycle_count - self.mirror_error_cycles > 10
					or self.cycle_count - self.lens_error_cycles > 10
					or self.cycle_count - self.vcm_error_cycle > 10
					or self.cycle_count - self.vcm_lense_error_cycle > 10):
				print "Test has stopped due to 10 consecutive wrong data"
				self.stop = True
			try:
				self.raw_log_file_ref = open("{}_raw_data.csv".format(self.adb_device_id), "a+")

			except IOError as err:
				print "File is not accessible {}".format(err)
			time.sleep(0.2)

			if self.run_VCM == 1:
				raw_vcm_data = self.multi_module_move(self.mode_select_VCM)
				print "VCM araw", raw_vcm_data
			if self.run_M == 1:
				raw_M_data = self.multi_module_move(self.mode_select_mirror)
				print "M raw", raw_M_data

		# Data validation based on run mode
			# if self.run_VCM == 1 and self.run_L == 0 and self.run_M == 0:
			# 	raw_vcm_data = self.multi_module_move(self.mode_select_VCM)
			# 	tmp_data_1 = self.calculate_positions(raw_vcm_data, self.mode_select_VCM)
			# 	if len(tmp_data_1) == 10:  # 5 lens with 2 HS`s
			# 		data_vcm = tmp_data_1
			# 	else:
			# 		print "VCM data valiadation Failed", tmp_data_1
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + "," + str(raw_vcm_data) + "\n"))
			#
			# elif self.run_L == 1 and self.run_VCM == 0 and self.run_M == 0:
			# 	raw_lens_data = self.multi_module_move(self.mode_select_lens)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + ",,,,," + str(raw_lens_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_lens_data, self.mode_select_lens)
			# 	if len(tmp_data_1) == 22:  # 11 lense with 2 HS`s
			# 		data_lens = tmp_data_1
			# 	else:
			# 		print "Lens data validation Failed", tmp_data_1
			#
			# elif self.run_M == 1 and self.run_VCM == 0 and self.run_L == 0:
			# 	raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + ",,,,,,,,," + str(raw_mirr_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
			# 	if len(tmp_data_1) == 16:  # 8 mirrors with 2 HS`s
			# 		data_mirr = tmp_data_1
			# 	else:
			# 		print "Mirror data validation is Failed", tmp_data_1
			#
			# elif self.run_VCM == 1 and self.run_L == 1 and self.run_M == 0:
			# 	raw_vcm_lens_data = self.multi_module_move(self.mode_select_VCM_lens)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + "," + str(raw_vcm_lens_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_vcm_lens_data, self.mode_select_VCM_lens)
			# 	if len(tmp_data_1) == 32:  # 5+11 actuators with 2 HS`s
			# 		data_vcm_lens = tmp_data_1
			# 	else:
			# 		print "vcm and lens data validation Failed", tmp_data_1
			#
			# elif self.run_VCM == 1 and self.run_M == 1 and self.run_L == 0:
			# 	raw_vcm_data = self.multi_module_move(self.mode_select_VCM)
			# 	raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + "," + str(raw_vcm_data) + ",,,,," + str(raw_mirr_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_vcm_data, self.mode_select_VCM)
			# 	tmp_data_2 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
			# 	if len(tmp_data_1) == 10 and len(tmp_data_2) == 16:  # 5 lens and mirrors with 2 HS`s
			# 		data_vcm = tmp_data_1
			# 		data_mirr = tmp_data_2
			# 	else:
			# 		print "VCM and mirr data verification failed", len(data_vcm), len(data_mirr)
			#
			# elif self.run_L == 1 and self.run_M == 1 and self.run_VCM == 0:
			# 	raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
			# 	raw_lens_data = self.multi_module_move(self.mode_select_lens)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + ",,,,," + str(raw_lens_data) + "," + str(raw_mirr_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
			# 	tmp_data_2 = self.calculate_positions(raw_lens_data, self.mode_select_lens)
			# 	if len(tmp_data_1) == 16 and len(tmp_data_2) == 22:  # 8 mirrors anf 11 lenses with 2 HS`s
			# 		data_mirr = tmp_data_1
			# 		data_lens = tmp_data_2
			# 	else:
			# 		print "M and L data validation failed", tmp_data_1, tmp_data_2
			#
			# elif self.run_VCM == 1 and self.run_M == 1 and self.run_L == 1:
			# 	raw_mirr_data = self.multi_module_move(self.mode_select_mirror)
			# 	raw_vcm_lens_data = self.multi_module_move(self.mode_select_VCM_lens)
			# 	self.raw_log_file_ref.write(
			# 		(str(self.cycle_count) + "," + str(raw_vcm_lens_data) + ",,,,," + str(raw_mirr_data) + "\n"))
			# 	tmp_data_1 = self.calculate_positions(raw_mirr_data, self.mode_select_mirror)
			# 	tmp_data_2 = self.calculate_positions(raw_vcm_lens_data, self.mode_select_VCM_lens)
			# 	if len(tmp_data_1) == 16 and len(tmp_data_2) == 32:  # 8 mirrors and 5 VCM + 11 lenses with 2 HS`s
			# 		data_mirr = tmp_data_1
			# 		data_vcm_lens = tmp_data_2
			# 	else:
			# 		print "All run data validation is failed"
			# time.sleep(0.2)
			#
			# if self.run_VCM + self.run_L == 2 or self.run_VCM + self.run_L + self.run_M == 3:
			# 	all_data = dict(data_vcm_lens.items() + data_mirr.items())
			# else:
			# 	all_data = dict(data_lens.items() + data_mirr.items() + data_vcm.items())
			# self.record_data(all_data)
			# self.file_ref.close()
			#
			if self.cycle_count % 10 == 0:
				print "%d cycles are done" % self.cycle_count
				print "%d minutes are passed" % ((time.time() - st_time) / 60)
				self.asic_reset()
				time.sleep(0.3)

			if str(self.read_battery_capcaity()).isdigit() and self.read_battery_capcaity() < 10:
				if not self.file_ref.closed:
					self.file_ref.close()
				print "Test paused due to critical battery, files are saved"
				while self.read_battery_capcaity() < 90 and not self.stop:
					self.is_paused = True
					self.do_charge(True)
					time.sleep(5)
				print "charge is done"
				self.asic_reset()
				self.is_paused = False
			self.file_ref.close()
		else:
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
		self.mainframe = Frame(master, width=500, height=200, bg="PeachPuff3")
		self.mainframe.grid(sticky=(N, W, E, S))
		self.tkvar = StringVar(self.mainframe)
		choices = self.test_module.get_dev_list()
		self.messages = [
			"Stopped", "Connected-", "Please connect!!!", "Stop cycle first!", "No device",
			"Running on", "Charging"]
		self.chk_but_var_dic = {}
		self.all_but_status = {}

		if choices is not None and len(choices) > 0:
			self.tkvar.set(choices[0])  # set the default option
		else:
			print "No connected devices"
			exit()

		# Drop down menu
		drop_down_menu = OptionMenu(self.mainframe, self.tkvar, *choices)
		drop_down_menu.grid(row=0, column=6, columnspan=2)
		drop_down_menu.configure(height=1, width=18)
		self.pop_up_lbl = Label(self.mainframe, text="Choose-")
		self.pop_up_lbl.grid(row=0, column=5)


		#  Configure layout
		for i_0 in range(8):
			self.mainframe.columnconfigure(i_0, weight=3, minsize=60)
		for i_1 in range(13):
			self.mainframe.rowconfigure(i_1, weight=1, minsize=40)

		but_exit = Button(self.mainframe, text="Exit", command=self.exit)
		but_exit.configure(height=2, width=10)
		but_exit.grid(column=7, row=6)

		self.bat_charge = Label(self.mainframe, text="Battery --%")
		self.bat_charge.grid(row=0, column=0, sticky=W)

		status_lbl = Label(self.mainframe, text="Test status", bg="PeachPuff3")
		status_lbl.config(font=("Courier", 14))
		status_lbl.grid(row=0, column=3, sticky=E, columnspan=2)

		self.run_status = Label(self.mainframe, text="Not Run")
		self.run_status.grid(row=1, column=3, columnspan=2)

		# TODO change possition
		self.live_status_lbl = Label(self.mainframe, text="        ")
		self.live_status_lbl.grid(row=2, column=3, columnspan=2)

		self.but_config()
		self.update_ui()

	def but_config(self):
		# Buttons function list
		func_list = \
			(self.connect, self.stop, self.show_vcm_graph, self.show_mirror_graph, self.show_lens_graph,
			self.run_test, self.open_logs)

		butt_name_list = \
			["Con./Stop/Disc.", "Stop", "VCM graph", "Mirror graph", "Lens graph", "Run Test", "Open logs"]

		chk_but_list = \
			["VCM", "Lens", "Mirror", "A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3","C3", "A4", "B4_f", "C4",
				"A5",   "B5", "C5_f", "C6_f"]

		for i in chk_but_list:
			self.chk_but_var_dic[i] = IntVar()
			self.chk_but_var_dic[i].set(0)

		i_bt = 0
		i_chkbt = 0

		for i_column in range(8):
			for i_row in range(1, 6):
				# Creating module group chekbuttons
				if i_column == 1 and i_row > 2:
					chk_but = Checkbutton(
						self.mainframe, text=chk_but_list[i_chkbt], var=self.chk_but_var_dic[chk_but_list[i_chkbt]])
					chk_but.grid(row=i_row, column=i_column)
					chk_but.config(height=1, width=4)
					i_chkbt +=1
				# Creating buttons
				elif i_column < 2 and i_row < 7:
					bt = Button(self.mainframe, text=butt_name_list[i_bt], command=func_list[i_bt])
					bt.configure(height=2, width=12)
					bt.grid(column=i_column, row=i_row)
					if i_bt < 6:
						i_bt += 1
				# Creating chebuttons
				elif 1 < i_column and i_row > 2:
					if i_column == 7 and (i_row == 3 or i_row == 4):
						continue
					chk_but = Checkbutton(
						self.mainframe, text=chk_but_list[i_chkbt], var=self.chk_but_var_dic[chk_but_list[i_chkbt]])
					i_chkbt += 1
					chk_but.grid(column=i_column, row=i_row, sticky=W)
					chk_but.config(height = 1, width=4)
		#print self.chk_but_var_dic["Mirror"].get()



	def dummy_func(self):
		pass

	def get_button_status(self):
		for i in self.chk_but_var_dic.keys():
			self.all_but_status[i] = self.chk_but_var_dic[i].get()
		return self.all_but_status


	def connect(self):
		self.test_module.connect()
		self.test_module.copy_lcc()
		self.test_module.copy_prog_app()
		self.bat_charge.config(text="Battery {}%".format(self.test_module.read_battery_capcaity()))
		self.tkvar.set(self.test_module.adb_device_id)

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
		self.live_status_lbl.config(bg="Red")

	def open_logs(self):
		subprocess.Popen(r'explorer /select, {}'.format(self.test_module.curr_path))

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
		#self.pop_up_lbl.update_idletasks()
		self.pop_up_lbl.after(1200, self.update_ui)
		if self.test_module.adb_device_id is None:
			# self.run_status.config(text=self.messages[2])
			self.live_status_lbl.config(text=self.messages[4])
		else:
			self.run_status.config(
				text=self.messages[1] + str(self.test_module.adb_device_id[-3:]))
		if self.test_module.is_runing:
			self.bat_charge.config(text="Battery {}%".format(self.test_module.bat_capacity))
			if not self.test_module.is_paused:
				self.live_status_lbl.config(
					text="{} cycles are done".format(self.test_module.cycle_count), bg="Green")
				# self.run_status.config(
				# 	text=(self.messages[5]+" {}".format(self.test_module.adb_device_id[-3:])), bg="Green")
			elif self.test_module.is_paused:
				pass
				# self.run_status.config(text=self.messages[6])
		elif not self.test_module.is_runing:
			self.live_status_lbl.config(text=self.messages[0], bg="Red")
			# self.run_status.config(bg="Red")
		if self.chk_but_var_dic["Mirror"].get == 0 and self.chk_but_var_dic["Lens"] == 0:
			self.chk_but_var_dic["B1"].set(1)

if debug:
	dut = CycleTest()
	dut.adb_device_id = "LFCLHMB7A1700596"
	print dut.read_battery_capcaity()


else:
	main_window = Tk()
	start_test_gui = GUI(main_window)
	main_window.mainloop()
	#print start_test_gui.get_button_status()
