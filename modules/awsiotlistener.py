#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard modules
import os

# user modules
from pyfw.appbase import AppBase
from paholistener import PahoListener

class AwsIoTListener(AppBase, object):

	def __init__(self, **kargs):
		# コンフィグ生成等
		super(AwsIoTListener, self).__init__(**kargs)

		self.logger = self.logging.getLogger(__name__)

		# 生成ファイルの場所、トークン一時
		path_temp = os.getcwd() + '/' + self.config['Application']['DIR_TEMP']
		self.logger.info(path_temp)
		# ディレクトリ存在チェック
		if not os.path.isdir(path_temp):
			os.mkdir(path_temp)

		# 待ち受けモジュール
		self.listener = PahoListener(
			paho = self.config['Paho'],
			pyaudio = self.config['pyaudio'],
			azure = self.config['Azure'],
			path_temp = path_temp,
			logging = self.logging,
			is_debug = kargs['is_debug'],
		)

	def run(self):
		"""
		メッセージ受信＆再生処理
		"""
		self.listener.run()
