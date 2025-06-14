import torch
import hiwonder.Camera as Camera
import cv2
import time

MODEL_PATH = '/home/pi/yolov5/yolov5s.pt'  # 确保路径正确

def main():
    cam = Camera.Camera()
    cam.camera_open()

    # 从本地 yolov5 代码库加载自定义权重
    model = torch.hub.load('/home/pi/yolov5', 'custom', path=MODEL_PATH, source='local')
    model.eval()

    while True:
        ret, frame = cam.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        results = model(frame)  # 直接传入BGR图像，yolov5内部会转成RGB并resize

        # 结果渲染
        img_result = results.render()[0]

        cv2.imshow('YOLOv5 Detection', img_result)

        if cv2.waitKey(1) == 27:
            break

    cam.camera_close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
