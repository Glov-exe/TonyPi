# ita_ws_python.py
import websocket
import json
import base64
import hashlib
import hmac
from urllib.parse import urlencode
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import _thread as thread
from queue import Queue
import ssl

STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2

class Ws_Param:
    def __init__(self, APPID, APIKey, APISecret):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1, "vad_eos":10000}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: ws-api.xfyun.cn\ndate: " + date + "\nGET /v2/iat HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode('utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        v = {"authorization": authorization, "date": date, "host": "ws-api.xfyun.cn"}
        return url + '?' + urlencode(v)

def Speech2text(audio_data, sample_rate=16000):
    queue = Queue()
    wsParam = Ws_Param(
        APPID='caf80acb',
        APISecret='NmM4YzkxYjBjMTI4ODIyYzA1Mjg0Njk2',
        APIKey='1f48e2e1a50809a0a30ba62833f5a2d0'
    )

    def on_message(ws, message):
        try:
            result = json.loads(message)
            if result["code"] == 0:
                text = "".join([w["w"] for i in result["data"]["result"]["ws"] for w in i["cw"]])
                print(f"识别结果: {text}")
                queue.put(text)
        except Exception as e:
            print("解析错误:", e)

    def on_error(ws, error):
        print("### 错误:", error)

    def on_close(ws, *args):
        print("### 连接关闭 ###")

    def on_open(ws):
        def run(*args):
            frameSize = 8000
            status = STATUS_FIRST_FRAME
            index = 0
            
            while index < len(audio_data):
                chunk = audio_data[index:index+frameSize]
                index += frameSize
                
                if status == STATUS_FIRST_FRAME:
                    data = {
                        "common": wsParam.CommonArgs,
                        "business": wsParam.BusinessArgs,
                        "data": {
                            "status": 0,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(chunk).decode('utf-8'),
                            "encoding": "raw"
                        }
                    }
                    status = STATUS_CONTINUE_FRAME
                elif index >= len(audio_data):
                    data = {
                        "data": {
                            "status": 2,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(chunk).decode('utf-8'),
                            "encoding": "raw"
                        }
                    }
                else:
                    data = {
                        "data": {
                            "status": 1,
                            "format": "audio/L16;rate=16000",
                            "audio": base64.b64encode(chunk).decode('utf-8'),
                            "encoding": "raw"
                        }
                    }
                
                ws.send(json.dumps(data))
                time.sleep(0.04)
            
            ws.close()

        thread.start_new_thread(run, ())

    ws = websocket.WebSocketApp(
        wsParam.create_url(),
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    try:
        return queue.get(timeout=10)
    except:
        return None