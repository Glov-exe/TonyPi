import torch
import cv2
import time
import sys
sys.path.append('/home/pi/yolov5-6.0')

# 模型加载
print("正在加载模型...")
model = torch.hub.load('/home/pi/yolov5-6.0', 'custom', path='/home/pi/yolov5n.pt', source='local')
print("模型加载完成")

# 设置模型为推理模式
model.eval()

# 打开摄像头
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("摄像头打开失败")
    exit()

print("摄像头打开成功，开始实时检测...")

while True:
    ret, frame = cap.read()
    if not ret:
        print("摄像头读取失败")
        break

    # 推理前时间戳
    start_time = time.time()

    # 进行推理，设置图像输入尺寸为 320x320
    results = model(frame, size=320)

    # 渲染结果
    annotated_frame = results.render()[0]

    # 显示结果
    cv2.imshow("YOLOv5 实时检测", annotated_frame)

    # 推理后耗时打印
    print(f"推理耗时：{(time.time() - start_time)*1000:.2f} ms")

    # 按 'q' 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
