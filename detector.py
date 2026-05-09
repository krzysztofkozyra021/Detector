import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
import os
from sign_mapping import get_sign_name, NUM_CLASSES, is_speed_limit


def preprocess_crop(crop, target_size=(64, 64), use_norm=False):
    resized = cv2.resize(crop, target_size)
    normalized = resized.astype("float32") / 255.0
    if use_norm:
        # Standard ImageNet normalization (very common for PyTorch models)
        mean = np.array([0.485, 0.456, 0.406], dtype="float32")
        std = np.array([0.229, 0.224, 0.225], dtype="float32")
        normalized = (normalized - mean) / std
    return normalized

def detect_signs(image, model, confidence_threshold=0.3):
    """
    Main detection function that uses the advanced TrafficSignDetector logic.
    """
    if model is None:
        raise ValueError("Model is not loaded.")

    height, width = image.shape[:2]
    is_small_image = width < 600 or height < 600
    
    # --- 1. Candidate Generation ---
    candidates = []
    
    # 1a. Edge-based candidates
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray_adj = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray_adj, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 200)
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    contours_edge, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 1b. Color-based candidates (HSV)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_ranges = [
        ([0, 50, 50], [15, 255, 255]),     # Red 1
        ([165, 50, 50], [180, 255, 255]),   # Red 2
        ([95, 60, 60], [135, 255, 255]),    # Blue
        ([10, 60, 60], [40, 255, 255])      # Yellow
    ]
    
    all_contours = list(contours_edge)
    for lower, upper in color_ranges:
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        all_contours.extend(cnts)

    # 1c. Process contours into candidates
    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < 400: continue # Min area from user script
        
        x, y, w, h = cv2.boundingRect(contour)
        if w < 20 or h < 20: continue
        
        if area > (width * height * 0.3): continue # Max 30% area
        
        aspect_ratio = float(w) / h
        if 0.5 < aspect_ratio < 2.0:
            candidates.append({"x": x, "y": y, "w": w, "h": h, "area": area})

    # 1d. Deduplicate candidates
    unique_candidates = []
    for cand in candidates:
        is_duplicate = False
        for uc in unique_candidates:
            if abs(cand["x"] - uc["x"]) < 10 and abs(cand["y"] - uc["y"]) < 10 and \
               abs(cand["w"] - uc["w"]) < 10 and abs(cand["h"] - uc["h"]) < 10:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_candidates.append(cand)
    candidates = unique_candidates

    # Always include full image for small crops
    if is_small_image or not candidates:
        has_full = any(c["x"] == 0 and c["y"] == 0 and c["w"] == width for c in candidates)
        if not has_full:
            candidates.append({"x": 0, "y": 0, "w": width, "h": height, "area": width * height})

    # --- 2. Classification ---
    is_pytorch = isinstance(model, torch.nn.Module)
    # The new system uses 32x32 for classification
    target_size = (32, 32) if is_pytorch else (64, 64)
    
    results = []
    speed_limits = []
    
    for cand in candidates:
        x, y, w, h = cand["x"], cand["y"], cand["w"], cand["h"]
        crop = image[y : y + h, x : x + w]
        if crop.size == 0: continue
        
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        processed = preprocess_crop(crop_rgb, target_size=target_size, use_norm=is_pytorch)
        
        if is_pytorch:
            device = next(model.parameters()).device
            input_tensor = torch.from_numpy(processed).permute(2, 0, 1).unsqueeze(0).float().to(device)
            with torch.no_grad():
                outputs = model(input_tensor)
                probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
        else:
            probs = model.predict(np.expand_dims(processed, 0), verbose=0)[0]
            
        class_id = int(np.argmax(probs))
        confidence = float(np.max(probs))
        
        # Log top prediction
        if confidence > 0.1:
            print(f"Candidate ({x},{y},{w},{h}): {get_sign_name(class_id)} ({confidence:.4f})")

        effective_threshold = confidence_threshold
        if x == 0 and y == 0 and w == width:
            effective_threshold = max(0.2, confidence_threshold - 0.1)
            
        if confidence >= effective_threshold:
            sign_info = {
                "class_id": class_id,
                "class_name": get_sign_name(class_id),
                "confidence": confidence,
                "bbox": {"x": x, "y": y, "w": w, "h": h, "area": w * h},
            }
            if is_speed_limit(class_id):
                speed_limits.append(sign_info)
            else:
                results.append(sign_info)

    # --- 3. Post-processing (NMS) ---
    if speed_limits:
        speed_limits.sort(key=lambda x: x["bbox"]["area"], reverse=True)
        results.append(speed_limits[0])

    results.sort(key=lambda x: x["confidence"], reverse=True)
    
    kept = []
    for res in results:
        overlap = False
        r_x, r_y, r_w, r_h, r_area = res["bbox"]["x"], res["bbox"]["y"], res["bbox"]["w"], res["bbox"]["h"], res["bbox"]["area"]
        for fin in kept:
            f_x, f_y, f_w, f_h, f_area = fin["bbox"]["x"], fin["bbox"]["y"], fin["bbox"]["w"], fin["bbox"]["h"], fin["bbox"]["area"]
            
            inter_x1 = max(r_x, f_x)
            inter_y1 = max(r_y, f_y)
            inter_x2 = min(r_x + r_w, f_x + f_w)
            inter_y2 = min(r_y + r_h, f_y + f_h)
            
            if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                union_area = float(r_area + f_area - inter_area)
                iou = inter_area / union_area
                if iou > 0.5: # Balanced NMS
                    overlap = True
                    break
        if not overlap:
            kept.append(res)

    return [
        {"class_name": r["class_name"], "confidence": round(r["confidence"], 4)}
        for r in kept
    ]
