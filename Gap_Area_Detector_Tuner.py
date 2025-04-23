import cv2
import numpy as np
import sys

# ─── USER SETUP ──────────────────────────────────────
IMG_PATH   = sys.argv[1] if len(sys.argv) > 1 else "screened_gaps/ST3_0007_fitc.jpg"
MAX_SHOW_W = 800    # max display width
MAX_SHOW_H = 600    # max display height
# ──────────────────────────────────────────────────────

def nothing(x): pass

# load image & green channel
img = cv2.imread(IMG_PATH)
if img is None:
    raise FileNotFoundError(f"Cannot load {IMG_PATH}")
green = img[:, :, 1]

# prepare windows
for name in ("Gap mask", "Dark mask", "Overlay", "Settings"):
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    if name != "Settings":
        cv2.resizeWindow(name, MAX_SHOW_W, MAX_SHOW_H)

# trackbars
cv2.createTrackbar("BlurK",  "Settings", 7,   51, nothing)
cv2.createTrackbar("Thresh", "Settings", 7,   255, nothing)
cv2.createTrackbar("DarkTh", "Settings", 5,   255, nothing)

print("Adjust sliders. ESC to quit.")

def show_fit(win, frame):
    """Down‑scale frame to fit within MAX_SHOW_W×MAX_SHOW_H if needed."""
    h, w = frame.shape[:2]
    scale = min(MAX_SHOW_W/w, MAX_SHOW_H/h, 1.0)
    if scale < 1.0:
        frame = cv2.resize(frame,
                           (int(w*scale), int(h*scale)),
                           interpolation=cv2.INTER_AREA)
    cv2.imshow(win, frame)

while True:
    # read sliders
    b = cv2.getTrackbarPos("BlurK",  "Settings")
    t = cv2.getTrackbarPos("Thresh", "Settings")
    d = cv2.getTrackbarPos("DarkTh", "Settings")
    bk = b if b % 2 == 1 else b + 1
    bk = max(bk, 1)

    # 1) gap mask on blurred green channel
    blur     = cv2.GaussianBlur(green, (bk, bk), 0)
    _, gap_m = cv2.threshold(blur, t, 255, cv2.THRESH_BINARY_INV)

    # 2) dark mask on original
    max_chan  = img.max(axis=2)
    dark_m    = max_chan <= d

    # 3) intersect
    final_m   = (gap_m == 255) & dark_m

    # 4) count percentage
    pct = final_m.sum() / final_m.size * 100

    # 5) build display frames
    disp_gap  = cv2.cvtColor(gap_m,  cv2.COLOR_GRAY2BGR)
    disp_dark = img.copy(); disp_dark[dark_m] = (0,0,255)
    overlay   = img.copy(); overlay[final_m] = (0,0,255)
    cv2.putText(overlay, f"{pct:.2f}% dark gaps", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    # 6) show all, scaled to fit
    show_fit("Gap mask",  disp_gap)
    show_fit("Dark mask", disp_dark)
    show_fit("Overlay",   overlay)
    cv2.imshow("Settings", np.zeros((1,400),dtype=np.uint8))  # just keep Settings alive

    if cv2.waitKey(50) & 0xFF == 27:
        break

cv2.destroyAllWindows()
