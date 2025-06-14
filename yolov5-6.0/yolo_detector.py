import torch
import cv2
import time
import sys
import os

class YOLOv5Detector:
    def __init__(self, model_dir, weights_path, image_size=320, camera_index=0):
        """
        初始化YOLOv5检测器
        :param model_dir: YOLOv5源码路径
        :param weights_path: 模型权重路径（如 .pt 文件）
        :param image_size: 推理图像尺寸
        :param camera_index: 摄像头索引（默认0）
        """
        self.image_size = image_size
        self.camera_index = camera_index

        print("正在加载模型...")
        sys.path.append(model_dir)
        self.model = torch.hub.load(model_dir, 'custom', path=weights_path, source='local')
        self.model.eval()
        print("模型加载完成")

    def start_detection(self):
        """启动实时摄像头检测"""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("摄像头打开失败")
            return

        print("摄像头打开成功，开始实时检测...")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("摄像头读取失败")
                break

            start_time = time.time()

            results = self.model(frame, size=self.image_size)
            annotated_frame = results.render()[0]

            cv2.imshow("YOLOv5 实时检测", annotated_frame)
            print(f"推理耗时：{(time.time() - start_time)*1000:.2f} ms")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# from yolo_detector import YOLOv5Detector

# detector = YOLOv5Detector(
#     model_dir='/home/pi/yolov5-6.0',
#     weights_path='/home/pi/yolov5n.pt',
#     image_size=320
# )

# detector.start_detection()
