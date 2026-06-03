import cv2
import numpy as np
import os

def get_safe_spam_points(screen_bytes):
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    h, w = screen.shape[:2]
    cx, cy = w // 2, h // 2

    safe_top = int(h * 0.12)
    safe_bottom = int(h * 0.65) 
    safe_left = int(w * 0.05)
    safe_right = int(w * 0.95)

    panic_points = []
    diamond_top = (cx, safe_top + 15)
    diamond_bottom = (cx, safe_bottom - 15)
    diamond_left = (safe_left + 15, cy)
    diamond_right = (safe_right - 15, cy)

    for progress in np.linspace(0, 1, 12):
        panic_points.append((int(diamond_top[0] + (diamond_left[0] - diamond_top[0]) * progress),
                             int(diamond_top[1] + (diamond_left[1] - diamond_top[1]) * progress)))
        panic_points.append((int(diamond_top[0] + (diamond_right[0] - diamond_top[0]) * progress),
                             int(diamond_top[1] + (diamond_right[1] - diamond_top[1]) * progress)))
        panic_points.append((int(diamond_bottom[0] + (diamond_left[0] - diamond_bottom[0]) * progress),
                             int(diamond_bottom[1] + (diamond_left[1] - diamond_bottom[1]) * progress)))
        panic_points.append((int(diamond_bottom[0] + (diamond_right[0] - diamond_bottom[0]) * progress),
                             int(diamond_bottom[1] + (diamond_right[1] - diamond_bottom[1]) * progress)))

    b = screen[:, :, 0].astype(np.int16)
    g = screen[:, :, 1].astype(np.int16)
    r = screen[:, :, 2].astype(np.int16)

    red_condition = (r > 110) & (r > g + 35) & (r > b + 35)
    red_mask = np.zeros((h, w), dtype=np.uint8)
    red_mask[red_condition] = 255

    ui_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(ui_mask, (safe_left, safe_top), (safe_right, safe_bottom), 255, -1)
    safe_red_mask = cv2.bitwise_and(red_mask, ui_mask)

    kernel = np.ones((15, 15), np.uint8)
    base_blob = cv2.dilate(safe_red_mask, kernel, iterations=2)

    red_pixels = cv2.findNonZero(base_blob)
    all_side_points = {}

    if red_pixels is not None:
        ext_top = red_pixels[red_pixels[:, :, 1].argmin()][0]
        ext_bottom = red_pixels[red_pixels[:, :, 1].argmax()][0]
        ext_left = red_pixels[red_pixels[:, :, 0].argmin()][0]
        ext_right = red_pixels[red_pixels[:, :, 0].argmax()][0]

        margin = 40
        safe_ext_top = (ext_top[0], max(safe_top, ext_top[1] - margin))
        safe_ext_bottom = (ext_bottom[0], min(safe_bottom, ext_bottom[1] + margin))
        safe_ext_left = (max(safe_left, ext_left[0] - margin), ext_left[1])
        safe_ext_right = (min(safe_right, ext_right[0] + margin), ext_right[1])

        def generate_line(pt1, pt2, num_points=12):
            return [(int(pt1[0] + (pt2[0]-pt1[0])*p), int(pt1[1] + (pt2[1]-pt1[1])*p)) for p in np.linspace(0, 1, num_points)]

        all_side_points["Top-Left"] = generate_line(safe_ext_left, safe_ext_top)
        all_side_points["Top-Right"] = generate_line(safe_ext_top, safe_ext_right)
        all_side_points["Bottom-Right"] = generate_line(safe_ext_right, safe_ext_bottom)
        all_side_points["Bottom-Left"] = generate_line(safe_ext_bottom, safe_ext_left)

    colored_mask = np.zeros_like(screen)
    colored_mask[base_blob > 0] = [255, 0, 0] 
    cv2.addWeighted(colored_mask, 0.3, screen, 1.0, 0, screen)
    cv2.rectangle(screen, (safe_left, safe_top), (safe_right, safe_bottom), (255, 255, 255), 1)

    colors = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0)] 
    for idx, (side_name, points) in enumerate(all_side_points.items()):
        color = colors[idx % len(colors)]
        for i in range(len(points) - 1):
            cv2.line(screen, points[i], points[i+1], color, 2) 
        for p in points:
            cv2.circle(screen, p, 5, color, -1)

    for p in panic_points:
        cv2.circle(screen, p, 4, (0, 165, 255), -1)

    if not os.path.exists("img"): os.makedirs("img")
    cv2.imwrite("img/tactical_map.png", screen)
    print(" [Scanner] Bounding Diamond saved to 'img/tactical_map.png'.")

    return all_side_points, panic_points