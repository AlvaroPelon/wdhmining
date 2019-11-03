#!/usr/bin/python
# coding=utf-8
# Escrito por Alvaro Rodriguez -> https://github.com/AlvaroPelon

import os, subprocess, requests, json, time, sys
from overclocking import Overclock
from flask import Flask
import multiprocessing

def connected_to_internet(url='http://www.google.com/', timeout=3):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet connection available.")
    return False

name = 'Mina5'

try:
	content = requests.get('http://192.168.1.16:2000/get_config', params={'mina': name}).content #Make GET request to get config info
	content = json.loads(content)['result'] # Parse JSON data from GET

	wallet = content[0]
	pool = content[1]
	ttemp = content[2]
	minfan = [3]

	if ttemp > 30 and ttemp <= 100:
		pass
	else:
		ttemp = '70'
	if minfan >= 0 and minfan <= 100:
		pass 
	else:
		minfan = minfan = '70'

except requests.exceptions.ConnectionError:
	print('No connection to main server, USING DEFAULT VALUES')
	wallet = '0xB34EE2CD1541976ebE56E6C89EF38e4BAB585277'
	pool = 'eu1.ethermine.org:4444'
	ttemp = '70' # ºC
	minfan = '70' # %

name = 'WDHMining'

class Miner():
	def OC(self):
		Overclock().overclock()
	def start_claymore(self):
		args = '-wd 1 -r 1 -epool {pool} -ewal {wallet}.{name} -esm 0 -epsw x -allpools 1 -tt {tt} -asm 1'.format(pool=pool, wallet=wallet, name=name, tt=ttemp, min_fanspeed=minfan)
		subprocess.Popen(['sudo /home/alvaro/claymore/ethdcrminer64 {args}'.format(args=args)], shell=True)
	def start_phx(self):
		args = '-pool {pool} -wal {wallet}.{name} -proto 3 -pass x -coin eth -cdm 2 -gt 11'.format(pool=pool, wallet=wallet, name=name)
		subprocess.Popen(['sudo /home/alvaro/phx/PhoenixMiner {args}'.format(args=args)], shell=True)
	def restartMiners(self):
		os.system('sudo killall ethdcrminer64')
		os.system('sudo killall PhoenixMiner')
		print('Killing miner...')
		self.OC()
		self.start()

app = Flask(__name__)
miner = Miner()

@app.route('/reload', methods=['POST'])
def reload():
	print('Reloading...')
	miner.restartMiner()
	return('', 204)
def runapp():
	app.run(debug=False, host='0.0.0.0', port=5555)

if __name__ == '__main__':
	uptime = os.popen("awk '{print $1}' /proc/uptime").readlines()[0].replace("\n", "")
	if float(uptime) < 60:
		while True:
			if connected_to_internet(): # Wait to have internet for the program to run
				print('Internet OK')
				break
			else:
				print('Check your internet connection!')
				time.sleep(1)
		try:
			p = multiprocessing.Process(target=runapp).start()
			try:
				
				miner.OC()
			except:
				print("Error during OC")
			miner.start_phx()
		except KeyboardInterrupt:
			raise SystemExit('Bye!')
	else:
		#print('Miner only runs at boot')
		sys.exit(1)

