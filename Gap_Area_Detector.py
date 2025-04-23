import os
import cv2
import numpy as np
from datetime import datetime

# ─── TUNED PARAMETERS ────────────────────────────
BLUR_K         = 15    # odd Gaussian kernel on the green channel
THRESH         = 35    # threshold on blurred green (gaps = white)
DARK_THRESHOLD = 21    # max(R,G,B) ≤ this → “true black” pixel
# ─────────────────────────────────────────────────

# ─── CHANGE THIS ONE LINE ───────────────────────
FILENAME = "ST3_0007_fitc.jpg"  # put your image name here
# ─────────────────────────────────────────────────

INPUT_DIR  = "screened_gaps"
OUTPUT_DIR = "output_area"

def process_image(path):
    img   = cv2.imread(path)
    green = img[:, :, 1]

    # 1) blur & threshold green to locate gaps
    blur, gap = cv2.GaussianBlur(green, (BLUR_K, BLUR_K), 0), None
    _, gap   = cv2.threshold(blur, THRESH, 255, cv2.THRESH_BINARY_INV)

    # 2) pure‑black mask on original RGB
    max_chan  = img.max(axis=2)
    dark_mask = max_chan <= DARK_THRESHOLD  # boolean array

    # 3) intersect: keep only black pixels inside gaps
    final_mask = (gap == 255) & dark_mask

    # 4) count & percentage
    total_px = final_mask.size
    dark_px  = int(final_mask.sum())
    pct_dark = dark_px / total_px * 100

    # 5) overlay & annotate
    out = img.copy()
    out[final_mask] = (0, 0, 255)
    cv2.putText(
        out,
        f"{pct_dark:.2f}% dark gaps",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
        cv2.LINE_AA
    )
    return out

def main():
    src_path = os.path.join(INPUT_DIR, FILENAME)
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"{FILENAME} not found in {INPUT_DIR}")

    result = process_image(src_path)

    # make timestamped output folder
    ts = datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    out_folder = os.path.join(OUTPUT_DIR, ts)
    os.makedirs(out_folder, exist_ok=True)

    # build new filename with "_gap_detected" before the extension
    base, ext = os.path.splitext(FILENAME)
    new_name  = f"{base}_gap_detected{ext}"

    dst_path = os.path.join(out_folder, new_name)
    cv2.imwrite(dst_path, result)
    print(f"✔ Processed '{new_name}' → '{dst_path}'")

if __name__ == "__main__":
    main()
