#!/usr/bin/python3
# coding=utf8
import time
import hiwonder.ASR as ASR
import hiwonder.TTS as TTS

def listen_via_asr():
    try:
        # 初始化语音识别和语音播报模块
        asr = ASR.ASR()
        tts = TTS.TTS()

        # 清空旧指令词，设置模式为关键词识别
        asr.eraseWords()
        asr.setMode(2)

        # 添加你需要的关键词和编号（编号可以自定义）
        asr.addWords(1, 'kai shi lu yin')  # 开始录音
        asr.addWords(2, 'jie shu lu yin')  # 结束录音

        # 语音提示
        tts.TTSModuleSpeak('', '语音录音模块已启动，请说：开始录音 或 结束录音')
        print("🟢 监听中：等待语音命令 “开始录音” 或 “结束录音”...")

        recording = False
        start_time = None

        while True:
            result = asr.getResult()

            if result:
                print("🎤 识别到命令 ID:", result)

                if result == 1 and not recording:
                    print("⏺️ 开始模拟录音中...")
                    tts.TTSModuleSpeak('', '开始录音')
                    recording = True
                    start_time = time.time()

                elif result == 2 and recording:
                    end_time = time.time()
                    duration = int(end_time - start_time)
                    print("⏹️ 录音结束，时长：{} 秒".format(duration))
                    tts.TTSModuleSpeak('', f'录音结束，共录了 {duration} 秒')
                    break

            if recording:
                elapsed = int(time.time() - start_time)
                print(f"[录音中] 已录制 {elapsed} 秒", end='\r')

            time.sleep(0.1)

    except Exception as e:
        print(" 错误：", e)

if __name__ == '__main__':
    listen_via_asr()
