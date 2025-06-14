import numpy as np
import pyaudio
import wave
import os
import json
import ssl
from queue import Queue
import websocket
from websocket._abnf import ABNF

# 科大讯飞语音识别参数配置
class Ws_Param:
    def __init__(self, APPID, APISecret, APIKey, AudioFile):
        self.APPID = APPID
        self.APISecret = APISecret
        self.APIKey = APIKey
        self.AudioFile = AudioFile
        
        # 固定参数
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {
            "language": "zh_cn",
            "domain": "iat",
            "accent": "mandarin",
            "vinfo": 1,
            "vad_eos": 10000
        }

    def create_url(self):
        from urllib.parse import urlencode
        import base64
        import hashlib
        import hmac
        import time
        
        url = "wss://iat-api.xfyun.cn/v2/iat"
        now = str(int(time.time()))
        m5 = hashlib.md5()
        m5.update((self.APPID + now).encode('utf-8'))
        m5str = m5.hexdigest()
        
        # 生成签名
        signature_origin = "host: " + "iat-api.xfyun.cn" + "\n"
        signature_origin += "date: " + now + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), 
                               signature_origin.encode('utf-8'), 
                               hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = 'api_key="%s", algorithm="%s", headers="%s", signature="%s"' % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 拼接请求参数
        v = {
            "authorization": authorization,
            "date": now,
            "host": "iat-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

# WebSocket回调函数
def on_error(ws, error):
    print("### 连接错误:", error)

def on_close(ws):
    print("### 连接关闭 ###")

def on_open(ws):
    def run(*args):
        # 读取音频文件并分块发送
        chunk_ms = 160  # 160ms的音频块
        chunk_size = int(16000 * 2 * chunk_ms / 1000)
        
        with open(wsParam.AudioFile, 'rb') as f:
            pcm = f.read()
        
        index = 0
        total = len(pcm)
        while index < total:
            end = index + chunk_size if (index + chunk_size) < total else total
            ws.send(pcm[index:end], ABNF.OPCODE_BINARY)
            index = end
            import time
            time.sleep(chunk_ms / 1000.0)
        
        # 发送结束标识
        ws.send('{"end": true}', ABNF.OPCODE_TEXT)
    
    import threading
    threading.Thread(target=run).start()

def on_message(ws, message):
    try:
        message = json.loads(message)
        code = message.get("code", 0)
        if code != 0:
            print(f"识别错误: {message.get('message')} (代码: {code})")
            queue.put("")
            return
        
        data = message["data"]["result"]["ws"]
        result = "".join([w["w"] for item in data for w in item["cw"]])
        queue.put(result)
    except Exception as e:
        print("解析结果异常:", e)
        queue.put("")

# 语音识别主函数
def Speech2text(audio_file):
    global queue, wsParam
    queue = Queue()
    
    # 替换为你的讯飞API凭证
    wsParam = Ws_Param(
        APPID='你的APPID',
        APISecret='你的APISecret',
        APIKey='你的APIKey',
        AudioFile=audio_file
    )
    
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(
        wsUrl,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    # 合并所有结果片段
    final_result = ""
    while not queue.empty():
        final_result += queue.get()
    
    return final_result.strip()

# 录音主函数
def record_audio():
    CHUNK = 256
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    OUTPUT_DIR = os.path.join(os.getcwd(), 'files')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    WAVE_OUTPUT_FILENAME = os.path.join(OUTPUT_DIR, 'Record.wav')
    
    # 录音参数
    mindb = 20       # 音量阈值
    delayTime = 15      # 小声持续周期数(约1秒)
    max_duration = 60   # 最长录制秒数
    
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    print("等待说话中... (音量超过阈值自动开始)")
    frames = []
    is_recording = False
    silent_counter = 0
    chunk_counter = 0
    max_chunks = max_duration * RATE // CHUNK
    
    try:
        while chunk_counter < max_chunks:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            current_volume = np.max(audio_data)
            
            # 音量检测逻辑
            if current_volume > mindb:
                if not is_recording:
                    print("\n检测到声音，开始录音...")
                is_recording = True
                silent_counter = 0
            elif is_recording:
                silent_counter += 1
            
            # 录音状态处理
            if is_recording:
                frames.append(data)
                print(f"\r录音中... 音量: {current_volume:5d} | 时长: {len(frames)*CHUNK/RATE:.1f}s", end="")
                
                # 静音超时停止
                if silent_counter > delayTime:
                    print("\n检测到静音，停止录音")
                    break
            chunk_counter += 1
        
        # 保存录音文件
        if len(frames) > 0:
            with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            print(f"录音已保存到: {WAVE_OUTPUT_FILENAME}")
            return WAVE_OUTPUT_FILENAME
        else:
            print("未检测到有效语音")
            return None
            
    except Exception as e:
        print(f"录音出错: {e}")
        return None
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    # 第一步：录音
    audio_file = record_audio()
    
    if audio_file:
        # 第二步：语音识别
        print("\n开始语音识别...")
        result = Speech2text(audio_file)
        print("\n识别结果:")
        print("▌" + "─"*(len(result)+2) + "▐")
        print("│ " + result + " │")
        print("▌" + "─"*(len(result)+2) + "▐")