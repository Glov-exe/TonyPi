#!/usr/bin/python3
# coding=utf8
import time
import cv2
import numpy as np
import os
import sys

import hiwonder.Camera as Camera
import hiwonder.yaml_handle as yaml_handle

# 颜色LAB阈值示例（根据你实际调试的yaml数据替换）
lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)

# 摄像头参数文件路径（按你原代码路径改）
sys.path.append("/home/pi/TonyPi/Functions")
from CameraCalibration.CalibrationConfig import calibration_param_path

# 读取畸变矫正参数
param_data = np.load(calibration_param_path + '.npz')
mtx = param_data['mtx_array']
dist = param_data['dist_array']
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

# 颜色映射，用于画框颜色
range_rgb = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'black': (0, 0, 0),
}

def get_max_contour(frame_lab, color):
    """获取指定颜色最大轮廓和面积"""
    lower = np.array(lab_data[color]['min'], dtype=np.uint8)
    upper = np.array(lab_data[color]['max'], dtype=np.uint8)
    mask = cv2.inRange(frame_lab, lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, 0

    max_contour = max(contours, key=cv2.contourArea)
    max_area = cv2.contourArea(max_contour)

    if max_area < 100:  # 过滤小面积噪声
        return None, 0

    return max_contour, max_area

def main():
    # 打开摄像头（用hiwonder库）
    my_camera = Camera.Camera()
    my_camera.camera_open()

    while True:
        ret, img = my_camera.read()
        if not ret or img is None:
            time.sleep(0.01)
            continue

        # 畸变矫正
        frame = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

        # 转LAB颜色空间
        frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

        detected_color = None
        detected_contour = None
        max_area = 0

        for color in ['red', 'green', 'blue']:  # 遍历颜色检测
            contour, area = get_max_contour(frame_lab, color)
            if area > max_area:
                max_area = area
                detected_color = color
                detected_contour = contour

        if detected_contour is not None:
            # 画最小外接圆
            (x, y), radius = cv2.minEnclosingCircle(detected_contour)
            center = (int(x), int(y))
            radius = int(radius)
            if radius > 5:
                cv2.circle(frame, center, radius, range_rgb[detected_color], 2)
                cv2.putText(frame, f"Color: {detected_color}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, range_rgb[detected_color], 2)
        else:
            cv2.putText(frame, "No color detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("Color Detection", frame)

        if cv2.waitKey(1) == 27:
            break

    my_camera.camera_close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
