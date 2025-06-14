#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time

# 保持原有模块路径不变
sys.path.append("/home/pi/TonyPi/HiwonderSDK")
from hiwonder.ActionGroupControl import runAction, runActionGroup

sys.path.append("/home/pi/TonyPi/Functions")
from learn.audio.luzhi import listen
from learn.audio.ita_ws_python import Speech2text

sys.path.append("/home/pi/TonyPi")
from Functions.Color_Recognize import run as color_detect


class VoiceControl:
    def __init__(self):
        # 完整动作指令映射
        self.action_mapping = {
            # 基本动作
            "站立": "stand",
            "立正": "stand",
            "前进": "go_forward",
            "后退": "back",
            "左转": "turn_left",
            "右转": "turn_right",
            "停止": "stand",
            
            # 表演动作
            "挥手": "wave",
            "鞠躬": "bow",
            "俯卧撑": "push_ups",
            "仰卧起坐": "sit_ups",
            "庆祝": "chest",
            "跳舞": "chest",
            
            # 武术动作
            "左勾拳": "left_uppercut",
            "右勾拳": "right_uppercut",
            "左侧踢": "left_kick",
            "右侧踢": "right_kick",
            "永春拳": "wing_chun",
            
            # 特殊动作
            "起立": "stand_up_front",
            "踏步": "stepping",
            "扭腰": "twist",

            # 特殊功能
            "颜色识别": "color_detect"
        }
        
        self.running = True

    def execute_action(self, action_name):
        """执行动作命令"""
        print(f"执行动作: {action_name}")
        try:
            if action_name in ['stand', 'squat']:  # 单动作
                runAction(action_name)
            else:  # 动作组
                runActionGroup(action_name, times=1, with_stand=True)
            return True
        except Exception as e:
            print(f"动作执行失败: {str(e)}")
            return False

    def process_command(self, text):
        """处理语音命令"""
        text = text.strip()
        print(f"识别到命令: {text}")

        # 检查退出命令
        if "关闭" in text or "退出" in text:
            print("收到关闭命令，退出程序...")
            self.running = False
            return True
            
        # 查找匹配动作
        for cmd, action in self.action_mapping.items():
            if cmd in text:
                return self.execute_action(action)
        
        print("未识别到有效命令")
        return False

    def run(self):
        """主控制循环"""
        print("语音控制系统已启动")
        print("可用命令:", ", ".join(self.action_mapping.keys()))
        
        try:
            while self.running:
                print("\n等待指令...")
                
                # 1. 录音
                listen()
                
                # 2. 语音识别
                print("正在识别...")
                recognized_text = Speech2text()
                
                # 3. 执行命令
                if recognized_text:
                    self.process_command(recognized_text)
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n系统已停止")

if __name__ == "__main__":
    vc = VoiceControl()
    vc.run()