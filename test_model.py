import cv2
import numpy as np
import torch
from model import load_trained_model
from detector import preprocess_crop
from sign_mapping import get_sign_name

model = load_trained_model("polskie_znaki_model_92.pth")
device = next(model.parameters()).device
img = cv2.imread("polish-dataset/classification/A2/1.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
processed_A = preprocess_crop(img_rgb, target_size=(32, 32), use_norm=True)
tensor_A = (
    torch.from_numpy(processed_A).permute(2, 0, 1).unsqueeze(0).float().to(device)
)
resized = cv2.resize(img_rgb, (32, 32), interpolation=cv2.INTER_AREA)
processed_B = resized.astype("float32") / 255.0
tensor_B = (
    torch.from_numpy(processed_B).permute(2, 0, 1).unsqueeze(0).float().to(device)
)
img_bgr = (
    cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA).astype("float32") / 255.0
)
tensor_C = torch.from_numpy(img_bgr).permute(2, 0, 1).unsqueeze(0).float().to(device)


def show_top5(tensor, label):
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0].cpu().numpy()
    top5 = np.argsort(probs)[-5:][::-1]
    print(f"\n--- {label} ---")
    for idx in top5:
        print(f"  {probs[idx] * 100:5.1f}%  {get_sign_name(idx)}")


show_top5(tensor_A, "A: aktualny preprocessing (CLAHE + ImageNet)")
show_top5(tensor_B, "B: tylko /255, RGB")
show_top5(tensor_C, "C: tylko /255, BGR")
