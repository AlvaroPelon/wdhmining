#!/usr/bin/python
# coding=utf-8
# Escrito por Alvaro Rodriguez -> https://github.com/AlvaroPelon

name = 'Mina5'

import requests, os, subprocess, json, sys
try:
	from termcolor import colored
except:
	pass
def colortext(text, color):
	try:
		return colored(text, color)
	except:
		return text 
class Server:
	def __init__(self, serverUrl):
		try:
			r = requests.get(url=serverUrl)
			self.content = r.content
		except requests.exceptions.ConnectionError:
			self.content = None
			return
	def get_content(self):
		if self.content != None:
			return json.loads(self.content)['result']
		else:
			return
class OS:
	def getGpuNumber(self):
		x = 0
		test = subprocess.check_output("""lspci | grep ' VGA ' | cut -d" " -f 1""", shell=True)
		lines = test.split('\n')
		for line in lines:
			x +=1
		if self.checkForiGPU():
			x -= 2
		else:
			x -= 1
		print('GPUs available: {x}'.format(x=x))
		return x
	def checkForiGPU(self):
		if 'Intel' in subprocess.check_output("""lspci -vnnn | perl -lne 'print if /^\d+\:.+(\[\S+\:\S+\])/' | grep VGA""", shell=True):
			print('iGPU detected')
			return True
		else:
			print('No iGPU detected')
			return False
class Overclock:
	def __init__(self):
		self.ocInfoDict = Server(serverUrl='http://192.168.1.16:2000/get_oc_info').get_content()
		self.GPUNumber = OS().getGpuNumber()
	def overclock(self):
		if self.ocInfoDict != None:
			for mina, settings in self.ocInfoDict.items():
				if mina == name:
					# AGRESSIVE UNDERVOLT
					for x in range(self.GPUNumber + 1):
						if settings[2] >= 800:
							print(colored('UNDERVOLTING...','yellow'))
							for y in range(14):
								os.system('/home/alvaro/overclocking/wolfamdctrl -i {x} --volt-state {y} --vddc-table-set {voltOC}'.format(x=x, y=y, voltOC=settings[2]))
						if settings[0] <= 1290 and settings[1] <= 2100 and settings[0] >= 1000 and settings[1] >= 1600:
							print(colored('--- Overclocking GPU {x} ---'.format(x=x), 'yellow'))

							string = os.popen('/home/alvaro/overclocking/wolfamdctrl -i {x} --core-state 7 --mem-state 2 --core-clock {coreOC} --mem-clock {memOC}'.format(x=x, coreOC=settings[0], memOC = settings[1])).read()
							if 'Specified' in string:
								print("Trying other mem_state")
								os.system('/home/alvaro/overclocking/wolfamdctrl -i {x} --core-state 7 --mem-state 1 --core-clock {coreOC} --mem-clock {memOC}'.format(x=x, coreOC=settings[0], memOC = settings[1]))
							#os.system('sudo echo manual > /sys/class/drm/card{x}/device/power_dpm_force_performance_level'.format(x=x))
							#os.system('sudo echo 7 > /sys/class/drm/card{x}/device/pp_dpm_sclk'.format(x=x))
							#os.system('sudo echo 2 > /sys/class/drm/card{x}/device/pp_dpm_mclk'.format(x=x))
						else:
							print('Invalid values for GPU {gpu_numb}, SKIPPING OC'.format(gpu_numb=x))
		else:
			print('No connection to main server, SKIPPING OC')
if __name__ == '__main__':
	Overclock().overclock()




