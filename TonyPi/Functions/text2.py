import pyaudio
from aip import AipSpeech
import webrtcvad
import collections
import audioop # 导入标准库 audioop

# --- 百度云平台配置 ---
# ⚠️ 请替换成你自己的密钥
APP_ID = '119228323'
API_KEY = 'GIGHwfRP4QeayOgxUo8OR55U'
SECRET_KEY = 'qGZlMwIa0pfqCjlAPXXJRR980JxCNw31'

# --- 音频参数 ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
ORIGINAL_RATE = 16000  # 使用麦克风支持的原始采样率进行录音
TARGET_RATE = 16000    # 定义百度API需要的目标采样率

CHUNK_DURATION_MS = 30  # VAD支持的块时长：10, 20, or 30
CHUNK_SIZE = int(ORIGINAL_RATE * CHUNK_DURATION_MS / 1000) # CHUNK_SIZE现在基于原始采样率计算
VAD_AGGRESSIVENESS = 1  # VAD敏感度：0-3，数值越高越不敏感

# --- 录音逻辑参数 ---
BUFFER_DURATION_S = 0.5 
SILENCE_DURATION_S = 1.2 

def recognize_chinese():
    """
    使用VAD进行智能录音，对音频进行重采样，并调用百度云API进行语音识别。
    返回识别到的中文字符串，如果失败则返回 None。
    """
    # 初始化百度AipSpeech客户端
    try:
        # 注意：请确保 APP_ID, API_KEY, SECRET_KEY 已被正确替换
        if '请替换' in APP_ID or '请替换' in API_KEY or '请替换' in SECRET_KEY:
            print("错误：请先在 text.py 文件中替换成您自己的百度云 API 密钥。")
            return None
        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    except Exception as e:
        print(f"初始化百度客户端失败: {e}")
        return None

    # 初始化VAD
    vad = webrtcvad.Vad()
    vad.set_mode(VAD_AGGRESSIVENESS)

    p = pyaudio.PyAudio()
    stream = None
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=ORIGINAL_RATE, # 使用原始采样率打开流
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)
        
        print("\n>>> 请开始说话...(检测到语音后会自动录音)")

        # 缓冲区大小也基于原始采样率
        ring_buffer_size = int(BUFFER_DURATION_S * ORIGINAL_RATE / CHUNK_SIZE)
        ring_buffer = collections.deque(maxlen=ring_buffer_size)
        
        triggered = False
        audio_frames = []
        
        silence_chunks = int(SILENCE_DURATION_S * 1000 / CHUNK_DURATION_MS)
        num_silent_chunks = 0

        while True:
            frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            # VAD检测时，也要使用正确的原始采样率
            is_speech = vad.is_speech(frame, ORIGINAL_RATE) 

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.8 * ring_buffer.maxlen:
                    triggered = True
                    print(">>> 检测到语音，正在录音...")
                    for f, s in ring_buffer:
                        audio_frames.append(f)
                    ring_buffer.clear()
            else:
                audio_frames.append(frame)
                if not is_speech:
                    num_silent_chunks += 1
                else:
                    num_silent_chunks = 0
                
                if num_silent_chunks > silence_chunks:
                    print(">>> 录音结束，正在处理音频...")
                    break
        
        # 将录音数据合并 (此时是48000Hz的)
        audio_data = b''.join(audio_frames)

        # --- [核心修改] 音频重采样 ---
        print(f">>> 正在将音频从 {ORIGINAL_RATE}Hz 重采样到 {TARGET_RATE}Hz...")
        sample_width = p.get_sample_size(FORMAT)
        resampled_audio_data, _ = audioop.ratecv(audio_data, sample_width, CHANNELS, ORIGINAL_RATE, TARGET_RATE, None)
        # -----------------------------

        print(">>> 正在识别...")
        # 调用百度语音识别API，使用重采样后的数据和目标采样率
        result = client.asr(resampled_audio_data, 'pcm', TARGET_RATE, {'dev_pid': 1537,})
        if result and result.get('err_no') == 0:
            print(f">>>语音识别结果... {result.get('result')[0]}")
            return result.get('result')[0]
        else:
            print("识别失败:", result)
            return None

    except Exception as e:
        print(f"发生错误: {e}")
        return None
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()
        print(">>> 资源已释放，等待下一次指令...")