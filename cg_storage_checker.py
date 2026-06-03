import cv2
import numpy as np
import pytesseract
import requests
import os
import time

# 1. Added IS_UPGRADE_WALL to your config imports
from config import (
    device,
    HOME_GOLD_REGION,
    HOME_ELIXIR_REGION,
    MAX_GOLD,
    MAX_ELIXIR,
    IS_UPGRADE_WALL  # Ensure this boolean is defined in config.py
)

# 2. Import the wall function we just built
from upgrade import find_and_click_lowest_cost_wall

# =========================================
# TELEGRAM CONFIG
# =========================================
BOT_TOKEN = "7706951596:AAGg9LF6TV3csG4AW6Q9qu7hmhZp67wHhpQ"
CHAT_ID = "#"

def check_home_loot():
    print("\n [Storage] Checking Home Village Vaults...")

    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)

    home_gold = _extract_home_number(screen, HOME_GOLD_REGION, "img/debug_home_gold.png")
    home_elixir = _extract_home_number(screen, HOME_ELIXIR_REGION, "img/debug_home_elixir.png")

    gold_percent = (home_gold / MAX_GOLD) * 100
    elixir_percent = (home_elixir / MAX_ELIXIR) * 100

    print(f"Gold: {home_gold:,}/{MAX_GOLD:,} ({gold_percent:.1f}%)")
    print(f"Elixir: {home_elixir:,}/{MAX_ELIXIR:,} ({elixir_percent:.1f}%)")

    needs_upgrade = False
    if gold_percent >= 90 or elixir_percent >= 90:
        needs_upgrade = True

def send_telegram_message(message):
    """Send Telegram alert."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Telegram Error: {e}")


def _extract_home_number(screen, region, debug_filename):
    y1, y2, x1, x2 = region
    crop = screen[y1:y2, x1:x2]

    if crop.size == 0:
        return 0

    bigger = cv2.resize(
        crop,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(bigger, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        240,
        255,
        cv2.THRESH_BINARY_INV
    )

    # Ensure debug folder exists
    os.makedirs(os.path.dirname(debug_filename), exist_ok=True)
    cv2.imwrite(debug_filename, thresh)

    config_str = '--psm 7 -c tessedit_char_whitelist=0123456789 '
    text = pytesseract.image_to_string(
        thresh,
        config=config_str
    )

    clean_text = ''.join(filter(str.isdigit, text))
    return int(clean_text) if clean_text != "" else 0


def check_home_loot():
    """Send Telegram alert and handle conditional wall upgrading if storage is high."""
    print("\n [Storage] Checking Home Village Vaults...")

    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)

    # =========================================
    # READ STORAGE VALUES
    # =========================================
    home_gold = _extract_home_number(
        screen,
        HOME_GOLD_REGION,
        "img/debug_home_gold.png"
    )

    home_elixir = _extract_home_number(
        screen,
        HOME_ELIXIR_REGION,
        "img/debug_home_elixir.png"
    )

    # =========================================
    # CALCULATE %
    # =========================================
    gold_percent = (home_gold / MAX_GOLD) * 100
    elixir_percent = (home_elixir / MAX_ELIXIR) * 100

    print(f"Gold: {home_gold:,}/{MAX_GOLD:,} ({gold_percent:.1f}%)")
    print(f"Elixir: {home_elixir:,}/{MAX_ELIXIR:,} ({elixir_percent:.1f}%)")

    needs_upgrade = False

    # =========================================
    # ONLY SEND ALERT IF 90%+
    # =========================================
    if gold_percent >= 90 or elixir_percent >= 90:

        status_message = (
            "🚨 STORAGE ALERT 🚨\n\n"
            "🟡 GOLD STORAGE\n"
            f"Current: {home_gold:,}\n"
            f"Capacity: {MAX_GOLD:,}\n"
            f"Usage: {gold_percent:.1f}%\n\n"
            "🟣 ELIXIR STORAGE\n"
            f"Current: {home_elixir:,}\n"
            f"Capacity: {MAX_ELIXIR:,}\n"
            f"Usage: {elixir_percent:.1f}%\n\n"
        )

        # Individual warnings
        if gold_percent >= 90:
            status_message += "🚨 Gold Storage Near Full!\n"
            needs_upgrade = True

        if elixir_percent >= 90:
            status_message += "🚨 Elixir Storage Near Full!\n"
            needs_upgrade = True

        # SEND TELEGRAM ALERT
        send_telegram_message(status_message)
        print(" [Storage] Telegram alert sent!")
    else:
        print(" [Storage] Storage below 90%, no alert sent.")

    # =========================================================
    # 3. NEW CRITICAL CONDITIONAL INTELLIGENCE POINT
    # =========================================================
    if needs_upgrade:
        if IS_UPGRADE_WALL:
            print("\n [Trigger] Storage high! Initiating wall safety scan...")
            
            # Pass the live gold and elixir counts straight into the function!
            # We set max_taps=5, but the bot will auto-reduce this if your loot is too low.
            find_and_click_lowest_cost_wall(
                available_gold=home_gold, 
                available_elixir=home_elixir
               
            )
        else:
            print("\n [Trigger] Storage high but IS_UPGRADE_WALL is FALSE. Skipping.")

    return home_gold, home_elixir, needs_upgrade


def generate_home_calibration():
    print(" [Storage] Generating calibration image...")
    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)
    screen = cv2.imdecode(screen_arr, cv2.IMREAD_COLOR)

    gy1, gy2, gx1, gx2 = HOME_GOLD_REGION
    cv2.rectangle(screen, (gx1, gy1), (gx2, gy2), (0, 0, 255), 2)

    ey1, ey2, ex1, ex2 = HOME_ELIXIR_REGION
    cv2.rectangle(screen, (ex1, ey1), (ex2, ey2), (255, 0, 255), 2)

    os.makedirs("img", exist_ok=True)
    cv2.imwrite("img/home_calibration.png", screen)
    print(" [Storage] 'img/home_calibration.png' saved!")

    if os.path.exists("img/debug_home_elixir.png"):
        os.remove("img/debug_home_elixir.png")
    if os.path.exists("img/debug_home_gold.png"):
        os.remove("img/debug_home_gold.png")
    print(" [End] Deleted Resource images.")


if __name__ == "__main__":
    generate_home_calibration()
    check_home_loot()