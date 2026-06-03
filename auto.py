import cv2
import numpy as np
from ppadb.client import Client as AdbClient

# =========================================================
# CONFIG
# =========================================================

ADB_PORT = 5555

TEMPLATE_PATH = "11.png"

MATCH_THRESHOLD = 0.80

OUTPUT_IMAGE = "detected_result.png"

# =========================================================
# CONNECT ADB
# =========================================================

print("[INFO] Connecting to BlueStacks ADB...")

client = AdbClient(host="127.0.0.1", port=5037)

client.remote_connect("127.0.0.1", ADB_PORT)

device = client.device(f"127.0.0.1:{ADB_PORT}")

if device is None:
    print("[ERROR] Device not found")
    exit()

print("[INFO] Connected!")

# =========================================================
# LOAD TEMPLATE
# =========================================================

template = cv2.imread(TEMPLATE_PATH)

if template is None:
    print("[ERROR] Template image not found")
    exit()

template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

print("[INFO] Template loaded")

# =========================================================
# CAPTURE SCREENSHOT
# =========================================================

image = device.screencap()

image_array = np.frombuffer(image, dtype=np.uint8)

screen = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

print("[INFO] Screenshot captured")

# =========================================================
# MULTI SCALE TEMPLATE MATCHING
# =========================================================

best_match = 0
best_location = None
best_size = None

for scale in np.linspace(0.5, 1.5, 20):

    resized_template = cv2.resize(
        template_gray,
        None,
        fx=scale,
        fy=scale
    )

    h, w = resized_template.shape[:2]

    # Skip if template bigger than screen
    if h >= screen_gray.shape[0] or w >= screen_gray.shape[1]:
        continue

    result = cv2.matchTemplate(
        screen_gray,
        resized_template,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val > best_match:
        best_match = max_val
        best_location = max_loc
        best_size = (w, h)

# =========================================================
# RESULT
# =========================================================

print(f"[INFO] Best confidence: {best_match:.2f}")

if best_match >= MATCH_THRESHOLD:

    x, y = best_location

    w, h = best_size

    center_x = x + w // 2
    center_y = y + h // 2

    print("\n[FOUND] Town Hall detected!")
    print(f"[FOUND] X = {center_x}")
    print(f"[FOUND] Y = {center_y}")

    # =====================================================
    # DRAW BOX
    # =====================================================

    cv2.rectangle(
        screen,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        4
    )

    # Center point
    cv2.circle(
        screen,
        (center_x, center_y),
        8,
        (0, 0, 255),
        -1
    )

    # Text label
    cv2.putText(
        screen,
        "Town Hall",
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    # =====================================================
    # SAVE IMAGE
    # =====================================================

    cv2.imwrite(OUTPUT_IMAGE, screen)

    print(f"[INFO] Saved marked screenshot -> {OUTPUT_IMAGE}")

    # =====================================================
    # CLICK TOWN HALL
    # =====================================================

    device.shell(f"input tap {center_x} {center_y}")

    print("[INFO] Clicked Town Hall")

else:
    print("[INFO] Town Hall not found")