import cv2
import numpy as np
from gtsrb_mapping import get_sign_name


def is_speed_limit(class_id):
    """Returns True if the class ID represents a speed limit sign (GTSRB 0-8)."""
    return 0 <= class_id <= 8


def preprocess_crop(crop):
    """
    Resizes the crop to 64x64 and normalizes it for the CNN model.
    """
    resized = cv2.resize(crop, (64, 64))
    # Normalize to [0, 1]
    normalized = resized.astype("float32") / 255.0
    return normalized


def detect_signs(image, model, confidence_threshold=0.8):
    """
    Finds bounding boxes in the image using simple heuristics (contours),
    then classifies each crop.
    If the image is already a cropped sign, it will process the full image too.
    Filters out predictions below the confidence threshold.
    Applies the "closer speed limit has priority" rule.
    """
    if model is None:
        raise ValueError("Model is not loaded.")

    height, width = image.shape[:2]

    # Check if the image itself might just be a cropped sign
    # We always include the full image as a candidate bounding box.
    candidates = [{"x": 0, "y": 0, "w": width, "h": height, "area": width * height}]

    # Only try heuristic detection if the image is large enough
    if width > 100 and height > 100:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        # Dilate edges to close gaps
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)

        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h

            # Filter extremely small or extremely large boxes, or bad aspect ratios
            if w < 30 or h < 30:
                continue
            if area > 0.9 * (width * height):
                continue

            aspect_ratio = float(w) / h
            if 0.5 <= aspect_ratio <= 1.5:
                candidates.append({"x": x, "y": y, "w": w, "h": h, "area": area})

    # Prepare batch prediction to optimize inference
    crops = []
    boxes = []

    for cand in candidates:
        x, y, w, h = cand["x"], cand["y"], cand["w"], cand["h"]

        # Enforce minimum size of 64x64 strictly as per requirements?
        # The requirement says "Minimalna rozdzielczość znaku na obrazie: 64x64 px"
        # So we can skip crops that are smaller than 64x64 to enforce this.
        if w < 64 or h < 64:
            continue

        crop = image[y : y + h, x : x + w]

        # Sometimes due to bounds we get empty crops
        if crop.size == 0:
            continue

        # Convert BGR (OpenCV) to RGB (Keras expects RGB usually)
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

        processed = preprocess_crop(crop_rgb)
        crops.append(processed)
        boxes.append(cand)

    if not crops:
        return []

    crops_array = np.array(crops)

    # Predict all candidates
    predictions_raw = model.predict(crops_array, verbose=0)

    results = []
    speed_limits = []

    for i, probs in enumerate(predictions_raw):
        class_id = int(np.argmax(probs))
        confidence = float(np.max(probs))

        if confidence >= confidence_threshold:
            sign_info = {
                "class_id": class_id,
                "class_name": get_sign_name(class_id),
                "confidence": confidence,
                "bbox": boxes[i],
            }

            if is_speed_limit(class_id):
                speed_limits.append(sign_info)
            else:
                results.append(sign_info)

    # Handle Speed Limit Priority: if multiple speed limits, keep the one with the largest area (closest)
    if speed_limits:
        # Sort speed limits by area descending
        speed_limits.sort(key=lambda x: x["bbox"]["area"], reverse=True)
        # Add the largest one to results
        results.append(speed_limits[0])
        # The others are discarded as per the requirement: "priorytet ma znak bliższy"

    # NMS (Non-Maximum Suppression) to remove duplicate detections of the same sign
    # We sort by confidence
    results.sort(key=lambda x: x["confidence"], reverse=True)
    final_results = []

    for res in results:
        overlap = False
        r_x, r_y, r_w, r_h = (
            res["bbox"]["x"],
            res["bbox"]["y"],
            res["bbox"]["w"],
            res["bbox"]["h"],
        )
        r_area = res["bbox"]["area"]

        for fin in final_results:
            f_x, f_y, f_w, f_h = (
                fin["bbox"]["x"],
                fin["bbox"]["y"],
                fin["bbox"]["w"],
                fin["bbox"]["h"],
            )
            f_area = fin["bbox"]["area"]

            # Intersection
            inter_x1 = max(r_x, f_x)
            inter_y1 = max(r_y, f_y)
            inter_x2 = min(r_x + r_w, f_x + f_w)
            inter_y2 = min(r_y + r_h, f_y + f_h)

            if inter_x1 < inter_x2 and inter_y1 < inter_y2:
                inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
                iou = inter_area / float(r_area + f_area - inter_area)

                if iou > 0.3:  # Significant overlap
                    overlap = True
                    break

        if not overlap:
            final_results.append(
                {
                    "class_name": res["class_name"],
                    "confidence": round(res["confidence"], 4),
                }
            )

    return final_results
