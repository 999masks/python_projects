#################################################
# Ligh L16 stress module test                   #
# current version V0.6                         #
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
#################################################

# TODO create plot at the and by sampling data at 100:1
# TODO implement failure check by defined criteris on the fly

import subprocess
import time
from time import strftime, localtime
from datetime import datetime
import struct
import re
from threading import Thread
#  from Tkinter import tkinter, Tk, Button, Label
from Tkinter import *
from matplotlib import pyplot as plt
from matplotlib.artist import setp


# debug = True
debug = False


def curr_time():
	return datetime.now().strftime("%H:%M:%S.%f")[:-3]


class StressTest:
	def __init__(self):
		self.current_version = "0.6"
		print "Module test programm, version 0.6"
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
		self.all_A_bitmask = " 3D 00 00"
		self.stop = False
		self.dev_list = []
		self.adb_device_id = None
		#self.adb_device_id = self.connect
		# self.copy_lcc()
		# self.copy_prog_app()
		self.cycle_count = 1
		self.all_mirr_data = None
		self.mir_result = {}
		self.lens_result = {}
		self.file_ref = None
		self.all_lens_data = None
		self.all_mirr_data = None
		self.charging_status = None
		self.raw_log_file_ref = None
		self.lens_current_cycle = 0
		self.mirror_current_cycle = 0
		self.lens_delta_header = "L_B1,L_B2,L_B3,L_B4,L_B5,L_C1,L_C2,L_C3,L_C4,L_C5,L_C6"
		self.mirror_delta_header = ",M_B1,M_B2,M_B3,M_B5,M_C1,M_C2,M_C3,M_C4"
		self.all_header = \
			"N_{},".format(strftime("%m-%d-%Y", localtime())) + "Time" + "," + \
			self.lens_delta_header + self.mirror_delta_header + "," + "B4 temp.,\n"
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
		self.all_lens_header = lens_list_hs1 + lens_list_hs2
		self.all_mirr_header = mirr_list_hs1 + mirr_list_hs2
		self.test_data = {}
		self.is_runing = False


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
				self.adb_device_id = dev_list[0]
				return dev_list[0]

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

	def move_mirrors(self):
		cmd = 'adb -s {} shell "./data/lcc {}"'.format(
			self.adb_device_id, (
				self.channel_sel_write + self.tran_id + self.mir_move_com_id +
				self.all_mir_bitmask + self.hs1_bit * 8))
		self.send_command(cmd)
		mirr_data_1 = self.read_mirr_position(1)
		time.sleep(0.2)
		cmd = 'adb -s {} shell "./data/lcc {}"'.format(
			self.adb_device_id, (
				self.channel_sel_write + self.tran_id + self.mir_move_com_id +
				self.all_mir_bitmask + self.hs2_bit * 8))

		self.send_command(cmd)
		mirr_data_2 = self.read_mirr_position(2)
		self.all_mirr_data = mirr_data_1 + mirr_data_2
		return self.all_mirr_data

	def move_lenses(self):
		cmd = 'adb -s {} shell "./data/lcc {}"'.format(
			self.adb_device_id,	(
				self.channel_sel_write + self.tran_id + self.lens_move_com_id +
				self.all_lens_bitmask + self.hs1_bit * 11))
		self.send_command(cmd)
		lens_data_1 = self.read_lens_position(1)
		time.sleep(0.2)
		cmd = 'adb -s {} shell "./data/lcc {}"'.format(
			self.adb_device_id, (
				self.channel_sel_write + self.tran_id + self.lens_move_com_id +
				self.all_lens_bitmask + self.hs2_bit * 11))
		self.send_command(cmd)
		lens_data_2 = self.read_lens_position(2)
		self.all_lens_data = lens_data_1 + lens_data_2
		return self.all_lens_data

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

	def read_mirr_position(self, hs):
		"""
		:param hs: hard stop 1 or 2
		:return: hard stop pos tag + 16 bit mirr position data
		"""
		all_mirr_pos = (
			'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_read + self.tran_id + self.mir_pos_com_id +
					self.all_mir_bitmask)))
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
		all_lens_pos = (
			'adb -s {} shell "./data/lcc {}"'.format(
				self.adb_device_id, (
					self.channel_sel_read + self.tran_id + self.lens_pos_com_id +
					self.all_lens_bitmask)))
		lens_positions = self.send_command(all_lens_pos)
		if hs == 1:
			lens_positions = [1] + ["".join([i.strip() for i in lens_positions])]
		elif hs == 2:
			lens_positions = [2] + ["".join([i.strip() for i in lens_positions])]
		return lens_positions

	def read_B4_tepmerature(self):
		cmd = 'adb -s {} shell "./data/lcc -C -m 0 -s 0 -r -p 01 00 1c 02"'.format(self.adb_device_id)
		read_temp = self.send_command(cmd)
		return str(self.convert_IEEE754_to_float(read_temp))

	def calculate_possitions(self, data, mir_or_len):
		"""
		:param data: for mirrors [
		0, "45100012000456078009800F011A0100", 1,
		45100012000456078009800F011A0100]
		for lenses [0, 32 bit data, 1, 32 bit data]
		:param mir_or_len: 1 mirror 2 lens
		:return: dic {L_B1_1:400', 'L_B2_1:400',..} or dic {M_B3_1:123', 'M_B4_1:322',..}
		"""
		i = 2
		item = None
		if mir_or_len == 1:  # mirror
			if len(data[1]) == 32 and len(data[3]) == 32:
				for item in self.all_mirr_header[:8]:
					hx1 = data[1][i - 2:i]
					i += 2
					hx2 = data[1][i -2:i]
					i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.mir_result[item] = value
				i = 2
				for item in self.all_mirr_header[8:]:
					hx1 = data[3][i - 2:i]
					i += 2
					hx2 = data[3][i - 2:i]
					i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.mir_result[item] = value
				self.mirror_current_cycle = 0
				return self.mir_result
			else:
				print "wrong data on mirrors {}".format(item)
				print "cycles:", self.cycle_count
				if self.mirror_current_cycle == 0:
					self.mirror_current_cycle = self.cycle_count
				return {}
		if mir_or_len == 2:  # lens
			if len(data[1]) == 44 and len(data[3]) == 44:
				for item in self.all_lens_header[:11]:
					hx1 = data[1][i - 2:i]
					i += 2
					hx2 = data[1][i - 2:i]
					i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.lens_result[item] = value
				i = 2
				for item in self.all_lens_header[11:]:
					hx1 = data[3][i - 2:i]
					i += 2
					hx2 = data[3][i - 2:i]
					i += 2
					try:
						value = self.convert_hex_to_dec((hx2 + hx1))
					except RuntimeError as err:
						print "Unable to read value {}".format(err)
						value = "--"
					self.lens_result[item] = value
				self.lens_current_cycle = 0
				return self.lens_result
			else:
				print "wrong data on lens {}".format(item)
				if self.lens_current_cycle == 0:
					self.lens_current_cycle = self.cycle_count
				return {}

	@staticmethod
	def convert_hex_to_dec(hx_data):
		hex_group = "0123456789abcdef"
		for i in hx_data:
			if not i.lower() in hex_group:
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
		if len(data) > 0:
			data_keys = data.keys()
			data_keys.sort()
			temp_row = ""
			delta_header = self.lens_delta_header + "," + self.mirror_delta_header
			n = 1
			for _ in delta_header.split(","):
				if n < len(data) + 1:
					if str(data[data_keys[n]]).isdigit() and str(data[data_keys[n - 1]]).isdigit():
						temp_row = temp_row + str(data[data_keys[n]]-data[data_keys[n-1]]) + ","

					else:
						temp_row = temp_row + "----" + ","
					n += 2
				else:
					break
			self.test_data[self.cycle_count] = temp_row + str(self.read_B4_tepmerature())

			try:
				self.file_ref = open((self.adb_device_id + "_actuator_log.csv"), "a+")
				self.file_ref.write(
					str(self.cycle_count) + "," + curr_time() + "," + temp_row +
					self.read_B4_tepmerature() + "\n")
			except IOError as err:
				print "File is not accessible {}".format(err)
			self.file_ref.close()
		#print "test date", self.test_data

	def reset(self):
		self.stop = False
		self.is_runing = False

	def plotting(self):
		if len(self.test_data) > 200:
			sampling_rate = 50
		else:
			sampling_rate = 1


		x_1 = range(1, (len(self.test_data) + 1))
		x_labels = []
		l__b4 = []
		L_B5 = []
		L_C1 = []
		l__c2 = []
		l__c3 = []
		l__c4 = []
		l__c5 = []
		l__c6 = []
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
					m__b1.append((self.test_data[cycles]).split(",")[11])
					m__b2.append((self.test_data[cycles]).split(",")[12])
					m__b3.append((self.test_data[cycles]).split(",")[13])
					m__b5.append((self.test_data[cycles]).split(",")[14])
					m__c1.append((self.test_data[cycles]).split(",")[15])
					m__c2.append((self.test_data[cycles]).split(",")[16])
					m__c3.append((self.test_data[cycles]).split(",")[17])
					m__c4.append((self.test_data[cycles]).split(",")[18])
					b4__temp.append((self.test_data[cycles]).split(",")[19])

		print "b1", m__b1, "b2", m__b2, "b3", m__b3, "b5", m__b5, "M_C1", m__c1, \
			"M_C2", m__c2, "M_C3", m__c3, "M_C4", m__c4, "B4_Temp", b4__temp

		fig = plt.figure()
		#host = fig.add_subplot(111)
		ax1 = plt.subplot2grid((6,1), (0,0))
		ax1.set_ylim(0, 900)  # core
		plt.title("L16 mirror test")
		plt.ylabel("delta")
		#plt.ylim(0, 900)
		ax2 = plt.subplot2grid((6, 1), (0, 0), sharex=ax1)
		plt.ylabel("Temper")

		ax2v = ax2.twinx()
		
		ax2 = ax2.twinx()
		ax3 = plt.subplot2grid((6, 1), (0, 0), sharex=ax1)
		par3 = ax2.twinx()
		par4 = ax2.twinx()
		par5 = ax2.twinx()
		par6 = ax2.twinx()
		par7 = ax2.twinx()
		par8 = ax2.twinx()
		# par2 = ax2.twinx()
		# par3 = ax2.twinx()
		# par4 = ax2.twinx()
		# par5 = ax2.twinx()
		# par6 = ax2.twinx()
		# par7 = ax2.twinx()
		# par8 = ax2.twinx()


		ax1.set_xlabel("Cycle")
		ax1.set_ylabel("Max mirror travel")
		ax2.set_ylabel("Temperature")
		# par2.set_ylabel("M-B2")
		# par3.set_ylabel("M-B3")
		# par4.set_ylabel("M-B5")
		# par5.set_ylabel("M-C1")
		# par6.set_ylabel("M-C2")
		# par7.set_ylabel("M-C3")
		# par8.set_ylabel("M-C4")



		# par1.set_ylim(-20,100)  # CCB

		color1 = plt.cm.viridis(2)
		color2 = plt.cm.magma(0.5)
		color3 = plt.cm.plasma(1.2)
		color4 = plt.cm.inferno(.7)
		color5 = plt.cm.viridis(1)
		color6 = plt.cm.magma(0.2)
		color7 = plt.cm.plasma(1.4)
		color8 = plt.cm.inferno(1.7)
		temp_color = plt.cm.inferno(.4)

		#plt.xticks(x_1, x_labels)
		#setp(host.get_xticklabels(), rotation=90)  # rotate time label

		p, = ax1.plot(x_1, b4__temp, color=temp_color, label="B4 Temp.")
		p1, = ax2.plot(x_1, m__b1, color=color2, label="M-B1")
		p2, = ax3.plot(x_1, m__b2, color=color3, label="M-B2")
		p3, = par3.plot(x_1, m__b3, color=color4, label="M-B3")
		p1, = par4.plot(x_1, m__b5, color=color2, label="M-B5")
		p2, = par5.plot(x_1, m__c1, color=color3, label="M-C1")
		p3, = par6.plot(x_1, m__c2, color=color4, label="M-C2")
		p1, = par7.plot(x_1, m__c3, color=color2, label="M-C3")
		p2, = par8.plot(x_1, m__c4, color=color3, label="M-C4")


		# legend in chart
		lns = [p, p1, p2, p3]
		ax1.legend(handles=lns, loc='best')

		# right, left, top, bottom
		ax2.spines['left'].set_position(('outward', 20))
		# par2.spines['right'].set_position(('outward', 40))


		ax1.yaxis.label.set_color(p.get_color())  # correct
		ax2.yaxis.label.set_color(p1.get_color())
		ax3.yaxis.label.set_color(p2.get_color())
		par3.yaxis.label.set_color(p3.get_color())

		plt.savefig("pyplot_multiple_y-axis.png", bbox_inches='tight')
		plt.title("L16 temeperature characterization. Serial:")
		plt.tight_layout()

		plt.show()


			# fig = plt.figure()
			# host = fig.add_subplot(111)

	def run_test(self):
		print "{} device is selected \n".format(self.adb_device_id)
		self.raw_log_file_ref = open("{}_raw_data.csv".format(self.adb_device_id), "a+")
		self.raw_log_file_ref.write("N cycles,,mirror data,,,,lense data \n")
		self.raw_log_file_ref.close()
		self.record_data_header()
		st_time = time.time()
		self.asic_reset()
		self.move_lenses()
		self.move_mirrors()
		while not self.stop:
			self.is_runing = True
			self.read_B4_tepmerature()
			time.sleep(0.2)
			if self.mirror_current_cycle != 0 and self.lens_current_cycle != 0 and (
								self.cycle_count - self.mirror_current_cycle > 10
						or self.cycle_count - self.lens_current_cycle > 10):
					print "Test has stopped due to 10 consecutive wrong data"
					self.stop = True
			raw_lens_data = self.move_lenses()
			data_lens = self.calculate_possitions(raw_lens_data, 2)
			raw_mirr_data = self.move_mirrors()
			data_mirr = self.calculate_possitions(raw_mirr_data, 1)
			try:
				with open(
						"{}_raw_data.csv".format(self.adb_device_id), "a+") as self.raw_log_file_ref:
					self.raw_log_file_ref.write(
						(str(self.cycle_count) + "," + str(raw_mirr_data) + "," + str(raw_lens_data) + "\n"))
			except IOError as err:
				print "File is not accessible {}".format(err)
			time.sleep(0.2)
			if data_lens and data_mirr and len(data_lens) == 22 and len(data_mirr) == 16:
				all_data = dict(data_lens.items() + data_mirr.items())
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
				while self.read_battery_capcaity() < 50:
					self.do_charge(True)
					time.sleep(300)
			self.cycle_count += 1
			self.file_ref.close()
		else:
			cmd = ""
			#move_actuator_to = raw_input("Do you want move actuator to HS1 or HS2? ")
			# if move_actuator_to.lower() == "hs1":
			# 	cmd = 'adb -s {} shell "./data/lcc {}"' \
			# 		.format(
			# 			self.adb_device_id,
			# 			(self.channel_sel_write + self.tran_id + self.mir_move_com_id +
			# 				self.all_mir_bitmask + self.hs1_bit * 8))
			# elif move_actuator_to.lower() == "hs2":
			# 	cmd = 'adb -s {} shell "./data/lcc {}"' \
			# 		.format(
			# 			self.adb_device_id,
			# 			(self.channel_sel_write + self.tran_id + self.mir_move_com_id +
			# 				self.all_mir_bitmask + self.hs2_bit * 8))
			# else:
			# 	print "Nothing is done at the end. The test is stoped"
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
		master.title("Stress modules")
		master.geometry("600x250")
		master.resizable(False, False)

		master.grid_rowconfigure(0, weight=1)
		master.grid_rowconfigure(1, weight=1)
		master.grid_columnconfigure(0, weight=1)
		mainframe = Frame(master, width=500, height=250, bg="PeachPuff3")
		mainframe.grid(sticky=(N, W, E, S))

		for i in range(5):
			mainframe.columnconfigure(i, weight=3, minsize=60)
		for i_1 in range(13):
			mainframe.rowconfigure(i_1, weight=1, minsize=45)


		self.test_module = StressTest()

		func_list = (self.connect, self.pause, self.stop, self.show_graph, self.run_test, self.open_logs)

		butt_name_list = ["Connect", "Pause", "Stop", "Show graph", "Run Test", "Open logs"]

		i = 0
		for i_column in range(2):
			for i_row in range(1,5):
					if i_column == 1 and 1 < i_row < 4:
						continue
					bt = Button(mainframe, text=butt_name_list[i], command=func_list[i])
					bt.configure(height=2, width=10)
					bt.grid(column=i_column, row=i_row, sticky = W)
					if i < 5:
						i += 1

		but_exit = Button(mainframe, text="Exit", command=self.exit)
		but_exit.configure(height=2, width=10)
		but_exit.grid(column=4, row=4)

	def connect(self):
		print "connected"
		self.test_module.connect()
		self.test_module.copy_lcc()
		self.test_module.copy_prog_app()

	def pause(self):
		pass

	def stop(self):
		self.test_module.stop = True

	def show_graph(self):
		self.test_module.plotting()

	def open_logs(self):
		pass

	def exit(self):
		sys.exit()

	def run_test(self):
		self.test_module.reset()
		#self.test_module.run_test()
		tr = Thread(target=self.test_module.run_test)
		tr.start()



window = Tk()
dut = GUI(window)

window.mainloop()

