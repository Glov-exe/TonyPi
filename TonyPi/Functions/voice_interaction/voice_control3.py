#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import time
import cv2
import numpy as np
import hiwonder.yaml_handle as yaml_handle

# 保持原有模块路径不变
sys.path.append("/home/pi/TonyPi/HiwonderSDK")
from hiwonder.ActionGroupControl import runAction, runActionGroup
sys.path.append("/home/pi/TonyPi/Functions")
from learn.audio.luzhi import listen
from learn.audio.ita_ws_python import Speech2text
sys.path.append("/home/pi/TonyPi")
from Functions.Color_Recognize import run as color_detect

# 在模块级别导入相机校准配置
try:
    from CameraCalibration.CalibrationConfig import calibration_param_path
except ImportError:
    calibration_param_path = None

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
        }
        
        # 特殊功能映射
        self.function_mapping = {
            "颜色识别": self.color_detection,
            "识别颜色": self.color_detection,
            "检测颜色": self.color_detection
        }
        
        self.running = True
        self.camera = None
        self.mapx = None
        self.mapy = None
        self.init_camera()
    
    def init_camera(self):
        """初始化摄像头"""
        try:
            if calibration_param_path is None:
                print("警告: 未找到相机校准配置")
                return
            
            # 加载参数
            param_data = np.load(calibration_param_path + '.npz')
            # 获取参数
            mtx = param_data['mtx_array']
            dist = param_data['dist_array']
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
            self.mapx, self.mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)
            
            open_once = yaml_handle.get_yaml_data('/boot/camera_setting.yaml')['open_once']
            if open_once:
                self.camera = cv2.VideoCapture('http://127.0.0.1:8080/?action=stream?dummy=param.mjpg')
            else:
                import hiwonder.Camera as Camera
                self.camera = Camera.Camera()
                self.camera.camera_open()
        except Exception as e:
            print(f"摄像头初始化失败: {str(e)}")
            self.camera = None
    
    def color_detection(self):
        """执行颜色识别功能"""
        print("开始颜色识别...")
        try:
            if self.camera is None:
                self.init_camera()
                if self.camera is None:
                    print("摄像头不可用")
                    return False
            
            # 运行5秒颜色识别
            end_time = time.time() + 20
            while time.time() < end_time:
                ret, img = self.camera.read()
                if img is not None:
                    frame = img.copy()
                    if self.mapx is not None and self.mapy is not None:
                        frame = cv2.remap(frame, self.mapx, self.mapy, cv2.INTER_LINEAR)  # 畸变矫正
                    frame = color_detect(frame)
                    cv2.imshow('Color Detection', frame)
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC键退出
                        break
                else:
                    time.sleep(0.01)
            
            cv2.destroyWindow('Color Detection')
            return True
        except Exception as e:
            print(f"颜色识别失败: {str(e)}")
            return False
    
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
        

        # 检查特殊功能命令
        for cmd, func in self.function_mapping.items():
            if cmd in text:
                return func()
        
        # 查找匹配动作
        for cmd, action in self.action_mapping.items():
            if cmd in text:
                return self.execute_action(action)
        
        print("未识别到有效命令")
        return False
    
    def cleanup(self):
        """清理资源"""
        # 调用颜色检测的退出函数
        
        if self.camera is not None:
            try:
                if hasattr(self.camera, 'camera_close'):
                    self.camera.camera_close()
                else:
                    self.camera.release()
                cv2.destroyAllWindows()
            except Exception as e:
                print(f"清理资源时出错: {str(e)}")
    
    def run(self):
        """主控制循环"""
        print("语音控制系统已启动")
        print("可用动作命令:", ", ".join(self.action_mapping.keys()))
        print("可用功能命令:", ", ".join(self.function_mapping.keys()))
        
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
        finally:
            self.cleanup()

if __name__ == "__main__":
    vc = VoiceControl()
    vc.run()