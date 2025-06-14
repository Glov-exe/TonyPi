#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
# 添加模块路径
#sys.path.append("/home/pi/TonyPi/HiwonderSDK/hiwonder")
#from ActionGroupControl import
# 添加模块路径
sys.path.append("/home/pi/TonyPi/HiwonderSDK")
from hiwonder.ActionGroupControl import runAction, runActionGroup

sys.path.append("/home/pi/TonyPi/Functions")
from learn.audio.luzhi import listen
from learn.audio.ita_ws_python import Speech2text

class VoiceControl:
    def __init__(self):
        self.commands = {
            "打开": self.open_action,
            "前进": self.move_forward,
            "后退": self.move_backward,
            "左转": self.turn_left,
            "右转": self.turn_right,
            "停止": self.stop_action
        }
        self.running = True
    
    def process_command(self, text):
        """处理识别到的语音命令"""
        print(f"识别到命令: {text}")
        
        # 首先检查是否是退出命令
        if "关闭" in text:
            print("收到关闭命令，退出程序...")
            self.running = False
            return True
            
        # 处理其他命令
        for cmd, action in self.commands.items():
            if cmd in text:
                action()
                return True
                
        print("未识别到有效命令")
        return False
    
    def run(self):
        """主运行循环"""
        print("语音控制系统已启动，等待指令...")
        try:
            while self.running:
                # 1. 录音
                print("\n请说话...")
                listen()
                
                # 2. 语音识别
                print("正在识别语音...")
                recognized_text = Speech2text()
                
                # 3. 处理命令
                if recognized_text:
                    self.process_command(recognized_text)
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n语音控制系统已停止")
    
    # 以下是各种动作方法
    def open_action(self):
        print("执行打开操作")
        # 这里可以添加实际的控制代码
    
    def move_forward(self):
        print("执行前进操作")
        # 这里可以添加实际的控制代码
    
    def move_backward(self):
        print("执行后退操作")
        # 这里可以添加实际的控制代码
    
    def turn_left(self):
        print("执行左转操作")
        # 这里可以添加实际的控制代码
    
    def turn_right(self):
        print("执行右转操作")
        # 这里可以添加实际的控制代码
    
    def stop_action(self):
        print("执行停止操作")
        # 这里可以添加实际的控制代码

if __name__ == "__main__":
    vc = VoiceControl()
    vc.run()