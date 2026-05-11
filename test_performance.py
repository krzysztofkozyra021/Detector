import time
import numpy as np
from model import load_trained_model
from detector import detect_signs


def test_performance():
    print("Loading model...")
    model = load_trained_model("model.h5")
    if model is None:
        print("Model not found. Run train.py first.")
        return
    img = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
    print("Warming up model...")
    _ = detect_signs(img, model)
    print("\nTesting Inference Time...")
    start = time.time()
    _ = detect_signs(img, model)
    end = time.time()
    inf_time_ms = (end - start) * 1000
    print(f"Inference Time: {inf_time_ms:.2f} ms")
    if inf_time_ms <= 500:
        print("PASS: Inference time <= 500 ms")
    else:
        print("FAIL: Inference time > 500 ms")
    print("\nTesting Repeatability (100 runs)...")
    results = []
    for _ in range(100):
        res = detect_signs(img, model)
        signature = tuple([(r["class_name"], round(r["confidence"], 2)) for r in res])
        results.append(signature)
    from collections import Counter

    counts = Counter(results)
    most_common = counts.most_common(1)[0]
    repeatability = (most_common[1] / 100) * 100
    print(f"Repeatability: {repeatability}%")
    if repeatability >= 95:
        print("PASS: Repeatability >= 95%")
    else:
        print("FAIL: Repeatability < 95%")


if __name__ == "__main__":
    test_performance()
