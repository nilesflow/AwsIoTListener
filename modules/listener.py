#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard modules
import os
import wave
import numpy as np

# user modules
from pyfw.libs import util
from pyfw.azure.cognitive import Cognitive
from pyfw.error.error import InternalError

# クラウドサーバ等の存在しないケース
try:
	import pyaudio
except ImportError:
	pass

class Listener:
	"""
	音声録音変換クラス
	"""

	# 出力音声ファイル名
	file_voice = 'transcribe.wav'

	def __init__(self, **kargs):
		self.logger = kargs['logging'].getLogger(__name__)

		# モジュール確認
		if not 'pyaudio' in globals():
			self.logger.error("can't find pyaudio.")
		self.audio = pyaudio.PyAudio()

		# 出力音声ファイルパス
		path = kargs['path_temp']
		
		# ディレクトリ存在チェック
		if not os.path.isdir(path):
			os.mkdir(path)

		self.path_voice = path + Listener.file_voice

		self.input_device_index = kargs['pyaudio']['input_device_index']

		# Cognitiveインスタンスを作成
		self.cognitive = Cognitive(
			key = kargs['azure']['SUBSCRIPTION_KEY'],
			path_temp = kargs['path_temp'],
			logging = kargs['logging']
		)

	def _record(self):
		chunk = 1024 * 20
		#サンプリングレート、マイク性能に依存
		RATE = 44100
		#録音時間
		RECORD_SECONDS = 10

		#マイク番号を設定: cat /proc/asound/modules
		input_device_index = self.input_device_index
		#マイクからデータ取得
		stream = self.audio.open(
			format = pyaudio.paInt16,
			channels = 1,
			rate = RATE,
			input = True,
			frames_per_buffer = chunk
		)
		try:
			# 録音処理
			sec_per_buffer = RATE / chunk
			SEC_STOP = 1.5
			threshold_start = 0.002 # 何か音が有ったら開始
			threshold_end	= 0.002 # 音がある程度無くなったら終了
			no_sound = 0
			recording = False
			all = []

			self.logger.info("recording...")
			for i in range(0, sec_per_buffer * RECORD_SECONDS):
				data = stream.read(chunk, False)

				# @refs https://qiita.com/mix_dvd/items/dc53926b83a9529876f7
				# 最大1に正規化
				x = np.frombuffer(data, dtype="int16") / 32768.0
				# 正負に伸びる、バラつきあるので平均化
				ave = np.average(np.absolute(x))
#				self.logger.info(str(i))
#				self.logger.info("x(cnt): " + str(len(x)))
				self.logger.info("x(ave): " + str(ave))
#				self.logger.info("x(max): " + str(x.max()))
#				self.logger.info("x(min): " + str(x.min()))
				if not recording:
					if ave > threshold_start:
						recording = True
				else:
					# 録音データを取得
					all.append(data)

					# 無音が暫く続いたら終了
					if ave < threshold_end:
						no_sound += 1
						if no_sound >= (sec_per_buffer * SEC_STOP):
							break;
					else:
						no_sound = 0

			stream.close()
			self.logger.info("recorded.")

		except Exception as e:
			stream.close()

			self.logger.critical(e)
			self.logger.critical(util.trace())
			raise e

		## ファイルが存在した場合は削除
		if os.path.isfile(self.path_voice):
			os.remove (self.path_voice)

		# 書き込み
		out = wave.open(self.path_voice, 'w')
		try:
			out.setnchannels(1) #mono
			out.setsampwidth(2) #16bits
			out.setframerate(RATE)
			out.writeframes(''.join(all))
			out.close()

		except Exception as e:
			out.close()

			self.logger.critical(e)
			self.logger.critical(util.trace())
			raise e


	def _transcribe(self):

		## ファイルチェック
		if not os.path.isfile(self.path_voice):
			raise InternalError("can't find sound file.")

		## 音声→テキスト
		data = open(self.path_voice, 'rb').read()
		self.text = self.cognitive.recognition(data)

	def listen(self):
		"""
		録音処理
		マイクで録音してファイルに保存、音声→テキスト変換
		"""
		self._record()
		self._transcribe()

		self.logger.info(self.text)
		return self.text

	def terminate(self):
		"""
		終了処理
		※プロセス起動したままなので、未使用
		"""
		self.audio.terminate()

