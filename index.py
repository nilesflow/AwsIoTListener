#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard modules
import sys, os

# 実行ディレクトリ＆モジュールパス設定
dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir)
sys.path.append(dir + '/modules')
sys.path.append(dir + '/user-packages')

# user modules
from pyfw.libs import util
from awsiotlistener import AwsIoTListener

is_debug = False

def run(is_daemon = False):
	AwsIoTListener(
		file_config = 'config.ini',
		is_daemon = is_daemon,
		is_debug = is_debug,
	).run()

def daemonize():
	pid = os.fork()
	if pid > 0:
		f = open('/var/run/aws-iot-listenerd.pid', 'w')
		f.write(str(pid) + "\n")
		f.close()
		sys.exit()

	elif pid == 0:
		run(True)

if __name__== '__main__':
	try:
		# コマンドライン引数を判定
		if '-d' in sys.argv:
			is_debug = True

		if '-D' in sys.argv:
			# デーモン起動
			daemonize()
		else:
			# 通常起動
			run(False)

	except Exception as e:
		print(e)
		print(util.trace())
