from openai import OpenAI
import sys
import os
sys.path.append("/home/pi/TonyPi/Functions")
import text2
import sys
sys.path.append('/home/pi/TonyPi/')
import time
from ActionGroupDict import *
import hiwonder.TTS as TTS
import hiwonder.ASR as ASR
import hiwonder.Board as Board
import hiwonder.ActionGroupControl as AGC
import hiwonder.yaml_handle as yaml_handle

# 替换为你自己的 API Key
client = OpenAI(
    api_key="sk-l0vRbOzyzS2OXvbWZNYYiAoJfCZoVwlO7aFfHelGqX0webkU", # 请务必使用你自己的有效Key
    base_url="https://api.moonshot.cn/v1",
)

def parse_complex_command(text: str) -> str:
    """
    将用户的自然语言指令分解成一个或多个标准机器人动作序列。
    返回的动作序列由英文逗号','分隔。
    """
    # 在Prompt中明确告知模型可用的标准动作，这能极大地提高准确性
    available_actions = "立正, 前进, 后退, 左移, 右移, 跳舞, 俯卧撑, 仰卧起坐, 左转, 右转, 挥手, 鞠躬, 下蹲, 庆祝, 左脚踢, 右脚踢, 永春, 左勾拳, 右勾拳, 左侧踢, 右侧踢, 前跌倒起立, 后跌倒起立, 扭腰, 原地踏步, 鞠躬"
    
    prompt = (f"可用的标准动作指令包括：'{available_actions}'。"
              f"请理解用户指令并将以下用户指令分解成一个由这些标准动作组成的序列，并用英文逗号','分隔。"
              f"如果指令无法分解或不包含任何有效动作，请返回空字符串。"
              f"用户指令：'{text}'")
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {
                "role": "system",
                "content": ("你是一个机器人指令解析器。你的任务是将用户的自然语言指令分解成一个或多个标准的机器人动作。"
                            "你只能返回标准的动作指令，多个指令之间用英文逗号','分隔。"
                            "不要添加任何解释、编号、空格或多余的文字。")
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.0,  # 对于指令转换，建议温度为0，以获得最稳定、最可预测的结果
    )
    return response.choices[0].message.content.strip()

def chat_with_ai(user_input: str) -> str:
    """
    与AI进行自然语言对话
    """
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {
                "role": "system",
                "content": ("你是一个智能机器人助手，能够与用户进行自然对话。"
                           "你的回答应该简洁明了，适合语音输出"
                           "如果用户询问你的能力，可以介绍你能执行的动作。")
            },
            {
                "role": "user",
                "content": user_input
            },
        ],
        temperature=0.7,  # 对话可以有些创造性
    )
    return response.choices[0].message.content.strip()

# 动作指令与ID的映射字典
action_map = {
    # 基本动作
    "立正": 1,        # stand_slow (原23)
    "前进": 2,        # go_forward (原1)
    "后退": 3,        # back_fast (原2)
    "左移": 4,        # left_move_fast (原3)
    "右移": 5,        # right_move_fast (原4)
    "左转": 8,        # turn_left (原7)
    "右转": 9,        # turn_right (原8)
    
    # 手势动作
    "挥手": 10,       # wave (原9)
    "鞠躬": 11,       # bow/jugong (原10/25)
    
    # 训练动作
    "俯卧撑": 6,     # push_ups (原5)
    "仰卧起坐": 7,   # sit_ups (原6)
    "下蹲": 12,      # squat (原11)
    
    # 格斗动作
    "左脚踢": 14,     # left_shot_fast (原13)
    "右脚踢": 15,     # right_shot_fast (原14)
    "永春": 16,      # wing_chun (原15)
    "左勾拳": 17,    # left_uppercut (原16)
    "右勾拳": 18,    # right_uppercut (原17)
    "左侧踢": 19,    # left_kick (原18)
    "右侧踢": 20,    # right_kick (原19)
    
    # 恢复动作
    "前跌倒起立": 21, # stand_up_front (原20)
    "后跌倒起立": 22, # stand_up_back (原21)
    
    # 其他动作
    "庆祝": 13,      # chest (原12)
    "扭腰": 23,      # twist (原22)
    "原地踏步": 25,  # stepping (原24)
    "跳舞": 26
}

if __name__ == "__main__":
    tts = TTS.TTS()
    tts.TTSModuleSpeak('', '准备就绪，请下达指令或与我对话')
    
    print("=== 机器人智能助手（Kimi） ===")
    print("可以下达动作指令（如'前进'或'跳舞'）或进行自然对话（如'你好'或'你会做什么'）")
    print("说'退出'来结束程序。\n")
    
    while True:
        # 获取用户语音输入
        user_input = text2.recognize_chinese()
        time.sleep(1)
 
        if not user_input:
            continue
            
        if "退出" in user_input:
            tts.TTSModuleSpeak('', '再见，主人')
            break
            
        print(f"接收到输入: '{user_input}'")
        
        try:
            # 首先尝试解析为动作指令
            command_sequence_str = parse_complex_command(user_input)
            
            if command_sequence_str:  # 如果是有效动作指令
                print(f"解析出的指令序列: {command_sequence_str}")
                
                # 分割指令
                if ',' in command_sequence_str:
                    commands = [cmd.strip() for cmd in command_sequence_str.split(',') if cmd.strip()]
                else:
                    commands = [cmd.strip() for cmd in command_sequence_str.split('，') if cmd.strip()]
                
                tts.TTSModuleSpeak('', '好的，收到，准备执行一系列动作')
                time.sleep(1.5)
                
                # 执行动作
                for command in commands:
                    if command in action_map:
                        action_id = action_map[command]
                        print(f"--> 正在执行: '{command}' (ID: {action_id})")
                        
                        tts.TTSModuleSpeak('', f'正在{command}')
                        
                        if command == "跳舞":
                            music_path = "/home/pi/TonyPi/audio/24.wav"
                            os.system("pkill aplay")
                            os.system(f"aplay {music_path} &")
                        
                        AGC.runActionGroup(action_group_dict[str(action_id - 1)], 1, True)
                        
                        if command == "跳舞":
                            os.system("pkill aplay")
                        
                        time.sleep(1.5)
                    else:
                        print(f"--> 未知指令: '{command}'，已跳过。")
                        tts.TTSModuleSpeak('', f"我不认识'{command}'这个动作")
                        time.sleep(1)
                
                tts.TTSModuleSpeak('', '所有动作已执行完毕')
                time.sleep(1)
            else:  # 如果不是动作指令，进行对话
                print("识别为对话内容")
                response = chat_with_ai(user_input)
                print(f"AI回复: {response}")
                tts.TTSModuleSpeak('', response)
                time.sleep(1)

        except Exception as e:
            print(f"发生错误: {e}")
            tts.TTSModuleSpeak('', '执行过程中出现了一点问题')
            time.sleep(1.5)