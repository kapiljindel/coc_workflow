import cv2
import numpy as np
import os
from config import DEBUG_MODE

# =====================================================================
# TACTICAL BOUNDARY CONFIGURATION (8 INDEPENDENT POINTS)
# Paste the X, Y coordinates from your Tkinter Base Scanner here!
# =====================================================================

# =====================================================================
# TACTICAL BOUNDARY CONFIGURATION (8 INDEPENDENT POINTS)
# =====================================================================

# 🟡 YELLOW LINE 
LINE_TL_START = (164, 420) # Line 1 (Top-Left) Start
LINE_TL_END   = (665, 61) # Line 1 (Top-Left) End

# 🟢 GREEN LINE
LINE_TR_START = (978, 78) # Line 2 (Top-Right) Start
LINE_TR_END   = (1419, 400) # Line 2 (Top-Right) End

# 🔴 PINK / MAGENTA LINE
LINE_BR_START = (1070, 711) # Line 3 (Bottom-Right) Start
LINE_BR_END   = (1437, 422) # Line 3 (Bottom-Right) End

# 🔵 CYAN / LIGHT BLUE LINE
LINE_BL_START = (129, 432) # Line 4 (Bottom-Left) Start
LINE_BL_END   = (495, 700) # Line 4 (Bottom-Left) End

# =====================================================================# =====================================================================

def get_safe_spam_points(screen_bytes):
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)
    h, w = screen.shape[:2]

    # Helper function to generate clickable points between ANY two distinct coordinates
    def generate_line(pt1, pt2, num_points=12):
        return [(int(pt1[0] + (pt2[0]-pt1[0])*p), int(pt1[1] + (pt2[1]-pt1[1])*p)) for p in np.linspace(0, 1, num_points)]

    # --- ADJUSTED FOR 4 INDEPENDENT LINES ---
    all_side_points = {}
    all_side_points["Top-Left"] = generate_line(LINE_TL_START, LINE_TL_END)
    all_side_points["Top-Right"] = generate_line(LINE_TR_START, LINE_TR_END)
    all_side_points["Bottom-Right"] = generate_line(LINE_BR_START, LINE_BR_END)
    all_side_points["Bottom-Left"] = generate_line(LINE_BL_START, LINE_BL_END)

    # Generate panic points directly from the independent lines
    panic_points = []
    for side_name, points in all_side_points.items():
        panic_points.extend(points) # Adds all 12 points of each line to the panic list

    # Process masks (Kept untouched for background color scanning logic)
    b = screen[:, :, 0].astype(np.int16)
    g = screen[:, :, 1].astype(np.int16)
    r = screen[:, :, 2].astype(np.int16)

    red_condition = (r > 110) & (r > g + 35) & (r > b + 35)
    red_mask = np.zeros((h, w), dtype=np.uint8)
    red_mask[red_condition] = 255

    kernel = np.ones((15, 15), np.uint8)
    base_blob = cv2.dilate(red_mask, kernel, iterations=2)

    if DEBUG_MODE:
        colored_mask = np.zeros_like(screen)
        colored_mask[base_blob > 0] = [255, 0, 0] 
        cv2.addWeighted(colored_mask, 0.3, screen, 1.0, 0, screen)

        # Draw the 4 independent lines and layout dots
        colors = [(0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0)] 
        for idx, (side_name, points) in enumerate(all_side_points.items()):
            color = colors[idx % len(colors)]
            # Draw the solid line segment
            cv2.line(screen, points[0], points[-1], color, 2) 
            
            # Draw the individual spam dots along the segment
            for p in points:
                cv2.circle(screen, p, 5, color, -1)

        # Draw panic points (slightly smaller/different color to distinguish if needed)
        for p in panic_points:
            cv2.circle(screen, p, 3, (0, 165, 255), -1)

        if not os.path.exists("img"): os.makedirs("img")
        cv2.imwrite("img/tactical_map.png", screen)
        print(" [Scanner] 8-Point Tactical Map saved to 'img/tactical_map.png'.")

    return all_side_points, panic_points