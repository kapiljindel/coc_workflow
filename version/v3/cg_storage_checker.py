import cv2
import numpy as np
import pytesseract
import requests

from config import (
    device,
    HOME_GOLD_REGION,
    HOME_ELIXIR_REGION,
    MAX_GOLD,
    MAX_ELIXIR
)

# =========================================
# TELEGRAM CONFIG
# =========================================
BOT_TOKEN = "7706951596:AAGg9LF6TV3csG4AW6Q9qu7hmhZp67wHhpQ"
CHAT_ID = "6316756859"


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

    cv2.imwrite(debug_filename, thresh)

    config_str = '--psm 7 -c tessedit_char_whitelist=0123456789 '

    text = pytesseract.image_to_string(
        thresh,
        config=config_str
    )

    clean_text = ''.join(filter(str.isdigit, text))

    return int(clean_text) if clean_text != "" else 0


def check_home_loot():
    """Send Telegram alert ONLY if Gold or Elixir is above 90%."""

    print("\n [Storage] Checking Home Village Vaults...")

    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)

    screen = cv2.imdecode(
        screen_arr,
        cv2.IMREAD_COLOR
    )

    # =========================================
    # READ STORAGE VALUES
    # =========================================
    home_gold = _extract_home_number(
        screen,
        HOME_GOLD_REGION,
        "debug_home_gold.png"
    )

    home_elixir = _extract_home_number(
        screen,
        HOME_ELIXIR_REGION,
        "debug_home_elixir.png"
    )

    # =========================================
    # CALCULATE %
    # =========================================
    gold_percent = (home_gold / MAX_GOLD) * 100
    elixir_percent = (home_elixir / MAX_ELIXIR) * 100

    print(
        f"Gold: {home_gold:,}/{MAX_GOLD:,} ({gold_percent:.1f}%)"
    )

    print(
        f"Elixir: {home_elixir:,}/{MAX_ELIXIR:,} ({elixir_percent:.1f}%)"
    )

    needs_upgrade = False

    # =========================================
    # ONLY SEND ALERT IF 90%+
    # =========================================
    if gold_percent >= 90 or elixir_percent >= 90:

        status_message = (
            "🚨 STORAGE ALERT 🚨\n\n"

            # "🟡 GOLD STORAGE\n"
            # f"Current: {home_gold:,}/{MAX_GOLD:,}\n"
            # f"Usage: {gold_percent:.1f}%\n\n"

            # "🟣 ELIXIR STORAGE\n"
            # f"Current: {home_elixir:,}\n"
            # f"Usage: {MAX_ELIXIR:.1f}%\n\n"
            # f"Usage: {elixir_percent:.1f}%\n\n"

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

    return home_gold, home_elixir, needs_upgrade


def generate_home_calibration():

    print(" [Storage] Generating calibration image...")

    screen_bytes = device.screencap()
    screen_arr = np.frombuffer(screen_bytes, np.uint8)

    screen = cv2.imdecode(
        screen_arr,
        cv2.IMREAD_COLOR
    )

    gy1, gy2, gx1, gx2 = HOME_GOLD_REGION

    cv2.rectangle(
        screen,
        (gx1, gy1),
        (gx2, gy2),
        (0, 0, 255),
        2
    )

    ey1, ey2, ex1, ex2 = HOME_ELIXIR_REGION

    cv2.rectangle(
        screen,
        (ex1, ey1),
        (ex2, ey2),
        (255, 0, 255),
        2
    )

    cv2.imwrite("home_calibration.png", screen)

    print(" [Storage] 'home_calibration.png' saved!")


if __name__ == "__main__":

    generate_home_calibration()

    check_home_loot()