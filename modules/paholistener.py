#!/usr/bin/env python
# -*- coding: utf-8 -*-

# standard modules
import json

# user modules
from pyfw.libs import util
from pyfw.pahoawsiot import PahoAwsIot
from pyfw.error.error import Error, ParamError
from pyfw.azure.error import RecognitionError

# local modules
from listener import Listener

class PahoListener(PahoAwsIot, object):

	def __init__(self, **kargs):
		super(PahoListener, self).__init__(
			topic_sub = kargs['paho']['MQTT_TOPIC_SUB'],
			ca = kargs['paho']['CA_ROOT_CERT_FILE'],
			cert = kargs['paho']['THING_CERT_FILE'],
			key = kargs['paho']['THING_PRIVATE_KEY'],
			host = kargs['paho']['MQTT_HOST'],
			port = kargs['paho']['MQTT_PORT'],
			keepalive = kargs['paho']['MQTT_KEEPALIVE_INTERVAL'],
			logging = kargs['logging']
		)

		self.listener = Listener(
			path_temp = kargs['path_temp'],
			azure = kargs['azure'],
			logging = kargs['logging']
		)

		self.topic_pub = kargs['paho']['MQTT_TOPIC_PUB']

		self.is_debug = kargs['is_debug']

	def _on_subscribe(self, mosq, obj, mid, granted_qos):
		self.logger.info("Subscribed to Topic with QoS: " + str(granted_qos))

		# test code
		if self.is_debug:
			self.publish(
				'raspberrypi/request/listen',
				request_id = util.uniqid(),
			)

	def _on_message(self, mosq, obj, msg):
		"""
		:param dict msg: dictionary converted from json
		 str  topic : raspberrypi/request/{action}
		 int  qos :
		 json payload : {"param1": "...", "param2": "..."}

		  action :
		   listen -- payload : null
		"""
		try:
			self.logger.info("Topic: " + str(msg.topic))
			self.logger.info("QoS: " + str(msg.qos))
			self.logger.info("Payload: " + str(msg.payload))

			ack = {}
			ack['sender'] = 'raspberrypi'

			# topic 確認
			# Level1:既定文字列のチェック
			levels_pub = msg.topic.split('/', 2)
			levels_sub = self.topic_sub.split('/')
			if levels_pub[0] != levels_sub[0]:
				raise ParamError("invalid topic.")

			# Level2：typeのチェック
			if levels_pub[1] != levels_sub[1]:
				raise ParamError("invalid type.")

			# Level3：actionのチェックと取得
			if len(levels_pub) < 3 :
				raise ParamError("can't find action.")
			action = levels_pub[2]

			# action毎の処理
			if action == 'listen':
				ack['action'] = 'listened'

				# 音声録音とテキスト変換
				result = self.listener.listen()
				ack['result'] = result

			# 処理終了
			self.logger.info('on message success.')

		except RecognitionError as e:
			# 通常変換失敗時
			self.logger.error(e.description)
			ack['result'] = "音声の聞き取りに失敗しました。"

		except Error as e:
			# その他ユーザエラー全般
			self.logger.error(e.description)
			ack['result'] = "録音処理中にエラーが発生しました。"

		except Exception as e:
			# その他エラー全般
			self.logger.critical(e)
			self.logger.critical(util.trace())
			ack['result'] = "録音処理中にエラーが発生しました。"

		# 応答返却
		self.publish(self.topic_pub, **ack)
		self.logger.info('on message complete.')

	def run(self):
		self.mqttc.loop_forever()
		pass

