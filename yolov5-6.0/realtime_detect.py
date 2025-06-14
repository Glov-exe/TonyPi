import cv2
import torch
from pathlib import Path
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords
from utils.plots import Annotator, colors
from utils.torch_utils import select_device

def detect_realtime(weights='yolov5s.pt', imgsz=640, conf_thres=0.25, iou_thres=0.45):
    # 初始化设备
    device = select_device('')
    model = attempt_load(weights, map_location=device)
    model.eval()
    stride = int(model.stride.max())
    names = model.module.names if hasattr(model, 'module') else model.names

    # 摄像头初始化
    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), '无法打开摄像头'

    while True:
        ret, frame = cap.read()
        if not ret:
            print("读取摄像头失败")
            break

        img = cv2.resize(frame, (imgsz, imgsz))
        img_tensor = torch.from_numpy(img).to(device)
        img_tensor = img_tensor.permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0)

        # 推理
        pred = model(img_tensor)[0]
        pred = non_max_suppression(pred, conf_thres, iou_thres)[0]

        annotator = Annotator(frame, line_width=2, example=str(names))
        if pred is not None and len(pred):
            pred[:, :4] = scale_coords(img_tensor.shape[2:], pred[:, :4], frame.shape).round()
            for *xyxy, conf, cls in pred:
                label = f'{names[int(cls)]} {conf:.2f}'
                annotator.box_label(xyxy, label, color=colors(int(cls), True))

        # 显示
        cv2.imshow('YOLOv5 Realtime Detection', annotator.result())
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    detect_realtime()
