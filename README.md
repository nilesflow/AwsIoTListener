# AwsIoTListener
AWS IoT MQTTのpublish messageで録音してAzureでテキスト変換
※ 音声->テキスト変換がAWS未対応なので、Azureを利用している

# 動作環境
Python 2.7.13 で確認

# 準備
RasperrryPI にマイクを接続
AWS IoT をセットアップ
Azure の Congnitive サービスをセットアップ

# セットアップ
```
sudo apt-get install alsa-utils sox libsox-fmt-all
sudo apt-get install python-pyaudio
amixer -c 1 sset Mic 100%
```
```
# pip install paho-mqtt  
# pip install boto3
```

```vi config.ini
# AWS IoTのHost、証明書情報を入力
# Azureへのアクセス情報を入力
# マイク番号を選択
```

# 起動方法
## シェル実行
```
python index.py
```
```
python index.py &
```

## デーモン起動
```
python index.py -D
```

## サービス起動
```
vi aws-iot-listenerd.service
# 下記パスを修正
ExecStart=/usr/bin/env python /path/to/AwsIoTListener/index.py -D
```
```
sudo cp aws-iot-listenerd.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start aws-iot-listenerd
sudo systemctl enable aws-iot-listenerd
```

# トラブルシューティング
再起動後マイクの音量が0に戻る場合は、起動スクリプトで下記を実行
```amixer -c 1 sset Mic 100%```
