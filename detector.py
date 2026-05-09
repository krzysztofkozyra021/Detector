import cv2
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
import os
from sign_mapping import get_sign_name, get_sign_code, NUM_CLASSES, is_speed_limit


def preprocess_crop(crop, target_size=(64, 64), use_norm=False):
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

    resized = cv2.resize(enhanced, target_size, interpolation=cv2.INTER_AREA)

    normalized = resized.astype("float32") / 255.0
    if use_norm:
        mean = np.array([0.485, 0.456, 0.406], dtype="float32")
        std = np.array([0.229, 0.224, 0.225], dtype="float32")
        normalized = (normalized - mean) / std
    return normalized


def color_matches_class(crop_bgr, class_id):
    code = get_sign_code(class_id)
    if not code:
        return True
    prefix = code[0]

    hsv = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2HSV)
    h_chan = hsv[:, :, 0]
    s_chan = hsv[:, :, 1]

    saturated_mask = s_chan > 70
    sat_pixels = saturated_mask.sum()
    total_pixels = saturated_mask.size

    if sat_pixels < 0.08 * total_pixels:
        return False

    hues = h_chan[saturated_mask]
    n = len(hues)

    red_pct = float(np.sum((hues < 15) | (hues > 165))) / n
    yellow_pct = float(np.sum((hues >= 15) & (hues < 40))) / n
    blue_pct = float(np.sum((hues >= 95) & (hues < 135))) / n
    green_pct = float(np.sum((hues >= 40) & (hues < 85))) / n

    if green_pct > 0.5:
        return False

    if prefix == "A":
        return (yellow_pct + red_pct) > 0.5
    if prefix == "B":
        return red_pct > 0.20 or blue_pct > 0.40
    if prefix == "C":
        return blue_pct > 0.40
    if prefix == "D":
        return blue_pct > 0.30 or green_pct > 0.30
    if prefix == "G":
        return red_pct > 0.20 or yellow_pct > 0.20

    return True


def boxes_same_object(b1, b2, iou_thresh=0.3, center_dist_ratio=0.5):
    x1 = max(b1["x"], b2["x"])
    y1 = max(b1["y"], b2["y"])
    x2 = min(b1["x"] + b1["w"], b2["x"] + b2["w"])
    y2 = min(b1["y"] + b1["h"], b2["y"] + b2["h"])

    if x1 < x2 and y1 < y2:
        inter = (x2 - x1) * (y2 - y1)
    else:
        inter = 0
    union = b1["area"] + b2["area"] - inter
    iou = inter / union if union > 0 else 0.0

    c1x = b1["x"] + b1["w"] / 2.0
    c1y = b1["y"] + b1["h"] / 2.0
    c2x = b2["x"] + b2["w"] / 2.0
    c2y = b2["y"] + b2["h"] / 2.0
    dist = ((c1x - c2x) ** 2 + (c1y - c2y) ** 2) ** 0.5
    avg_size = (b1["w"] + b1["h"] + b2["w"] + b2["h"]) / 4.0

    return iou > iou_thresh or dist < avg_size * center_dist_ratio


def is_dominated_by(small, large, margin=0.2):
    """
    Czy 'small' jest zdominowany przez 'large':
    - srodek 'small' jest wewnatrz 'large' (z marginesem)
    - 'small' jest istotnie mniejszy
    """
    if small["area"] >= large["area"] * 0.5:
        return False
    cx = small["x"] + small["w"] / 2.0
    cy = small["y"] + small["h"] / 2.0
    lx1 = large["x"] - large["w"] * margin
    ly1 = large["y"] - large["h"] * margin
    lx2 = large["x"] + large["w"] * (1 + margin)
    ly2 = large["y"] + large["h"] * (1 + margin)
    return lx1 <= cx <= lx2 and ly1 <= cy <= ly2


def detect_signs(image, model, confidence_threshold=0.85):
    if model is None:
        raise ValueError("Model is not loaded.")

    MIN_CONFIDENCE = confidence_threshold
    MIN_MARGIN = 0.50

    height, width = image.shape[:2]
    is_small_image = width < 600 or height < 600

    # Skala-zalezne minimum: znak nie moze byc mniejszy niz 2.5% mniejszego wymiaru
    min_dim = min(width, height)
    MIN_W = max(20, int(min_dim * 0.025))
    MIN_H = max(20, int(min_dim * 0.025))
    MIN_AREA = max(400, int(min_dim * min_dim * 0.0008))

    # --- 1. Candidate Generation ---
    candidates = []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_adj = clahe.apply(gray)
    blurred = cv2.GaussianBlur(gray_adj, (3, 3), 0)
    edges = cv2.Canny(blurred, 30, 200)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=2)
    contours_edge, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    color_ranges = [
        ([0, 50, 50], [15, 255, 255]),
        ([165, 50, 50], [180, 255, 255]),
        ([95, 60, 60], [135, 255, 255]),
        ([10, 60, 60], [40, 255, 255]),
    ]

    all_contours = list(contours_edge)
    for lower, upper in color_ranges:
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.dilate(mask, kernel, iterations=1)
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        all_contours.extend(cnts)

    for contour in all_contours:
        area = cv2.contourArea(contour)
        if area < MIN_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        if w < MIN_W or h < MIN_H:
            continue

        if area > (width * height * 0.3):
            continue

        aspect_ratio = float(w) / h
        if 0.5 < aspect_ratio < 2.0:
            candidates.append({"x": x, "y": y, "w": w, "h": h, "area": area})

    # Deduplikacja kandydatow (przed klasyfikacja)
    unique_candidates = []
    for cand in candidates:
        is_duplicate = False
        for uc in unique_candidates:
            if boxes_same_object(cand, uc, iou_thresh=0.5, center_dist_ratio=0.3):
                if cand["area"] > uc["area"]:
                    uc.update(cand)
                is_duplicate = True
                break
        if not is_duplicate:
            unique_candidates.append(dict(cand))
    candidates = unique_candidates

    if is_small_image or not candidates:
        has_full = any(
            c["x"] == 0 and c["y"] == 0 and c["w"] == width for c in candidates
        )
        if not has_full:
            candidates.append(
                {"x": 0, "y": 0, "w": width, "h": height, "area": width * height}
            )

    print(
        f"Min size: {MIN_W}x{MIN_H}, min area: {MIN_AREA}, "
        f"unikalnych kandydatow: {len(candidates)}"
    )

    # --- 2. Classification ---
    is_pytorch = isinstance(model, torch.nn.Module)
    target_size = (32, 32) if is_pytorch else (64, 64)

    results = []
    speed_limits = []

    for cand in candidates:
        x, y, w, h = cand["x"], cand["y"], cand["w"], cand["h"]

        pad_w = int(w * 0.1)
        pad_h = int(h * 0.1)

        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(width, x + w + pad_w)
        y2 = min(height, y + h + pad_h)

        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        processed = preprocess_crop(
            crop_rgb, target_size=target_size, use_norm=is_pytorch
        )

        if is_pytorch:
            device = next(model.parameters()).device
            input_tensor = (
                torch.from_numpy(processed)
                .permute(2, 0, 1)
                .unsqueeze(0)
                .float()
                .to(device)
            )
            with torch.no_grad():
                outputs = model(input_tensor)
                probs = torch.softmax(outputs, dim=1)[0].cpu().numpy()
        else:
            probs = model.predict(np.expand_dims(processed, 0), verbose=0)[0]

        sorted_probs = np.sort(probs)[::-1]
        top1 = float(sorted_probs[0])
        top2 = float(sorted_probs[1])
        margin = top1 - top2
        class_id = int(np.argmax(probs))
        confidence = top1

        if confidence < MIN_CONFIDENCE:
            continue
        if margin < MIN_MARGIN:
            continue

        color_ok = color_matches_class(crop, class_id)

        status = "OK" if color_ok else "REJECT-COLOR"
        print(
            f"  ({x},{y},{w},{h}): {get_sign_name(class_id)} "
            f"top1={top1:.3f} margin={margin:.3f} [{status}]"
        )

        if not color_ok:
            continue

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

    # --- 3. Post-processing ---
    if speed_limits:
        speed_limits.sort(key=lambda x: x["bbox"]["area"], reverse=True)
        results.append(speed_limits[0])

    results.sort(key=lambda x: x["confidence"], reverse=True)

    # Class-agnostic NMS
    kept = []
    for res in results:
        is_dup = False
        for fin in kept:
            if boxes_same_object(res["bbox"], fin["bbox"],
                                 iou_thresh=0.3, center_dist_ratio=0.5):
                is_dup = True
                break
        if not is_dup:
            kept.append(res)

    # Dominance suppression: malej detekcji wewnatrz duzej nie ma prawa byc
    final = []
    for r in kept:
        dominated = False
        for other in kept:
            if other is r:
                continue
            if other["confidence"] >= r["confidence"]:
                if is_dominated_by(r["bbox"], other["bbox"], margin=0.2):
                    dominated = True
                    print(
                        f"  Dominance: {r['class_name']} "
                        f"({r['bbox']['w']}x{r['bbox']['h']}) wewnatrz "
                        f"{other['class_name']} "
                        f"({other['bbox']['w']}x{other['bbox']['h']}) - usuniety"
                    )
                    break
        if not dominated:
            final.append(r)

    print(f"Po NMS+dominance zostalo: {len(final)}")

    return [
        {
            "class_name": r["class_name"],
            "confidence": round(r["confidence"], 4),
            "bbox": {
                "x": int(r["bbox"]["x"]),
                "y": int(r["bbox"]["y"]),
                "w": int(r["bbox"]["w"]),
                "h": int(r["bbox"]["h"]),
            },
        }
        for r in final
    ]