import customtkinter as ctk
import subprocess
import threading
import sys
import os
import json

# ==========================================
# APP SETTINGS
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# ==========================================
# LOAD CONFIG
# ==========================================

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "ADB_PORT": 5555,
            "MINIMUM_GOLD": 400000,
            "MINIMUM_ELIXIR": 400000,
            "TOTAL_TROOPS": 30,
            "MAX_GOLD": 160000000000,
            "MAX_ELIXIR": 365000000000000
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f, indent=4)

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


config = load_config()

# ==========================================
# MAIN WINDOW
# ==========================================

app = ctk.CTk()
app.geometry("650x700")
app.title("COC BOT CONTROL PANEL")

# ==========================================
# TITLE
# ==========================================

title = ctk.CTkLabel(
    app,
    text="COC BOT CONTROL PANEL",
    font=("Arial", 28, "bold")
)
title.pack(pady=20)

# ==========================================
# CONFIG FRAME
# ==========================================

config_frame = ctk.CTkFrame(app)
config_frame.pack(padx=20, pady=10, fill="both", expand=False)

entries = {}

for key, value in config.items():

    row = ctk.CTkFrame(config_frame)
    row.pack(fill="x", padx=10, pady=8)

    label = ctk.CTkLabel(
        row,
        text=key,
        width=220,
        anchor="w",
        font=("Arial", 14)
    )
    label.pack(side="left", padx=10)

    entry = ctk.CTkEntry(row, height=35)
    entry.insert(0, str(value))
    entry.pack(side="right", fill="x", expand=True, padx=10)

    entries[key] = entry

# ==========================================
# STATUS LABEL
# ==========================================

status_label = ctk.CTkLabel(
    app,
    text="READY",
    font=("Arial", 14)
)
status_label.pack(pady=10)

# ==========================================
# SAVE SETTINGS
# ==========================================

def save_settings():

    new_config = {}

    for key, entry in entries.items():

        value = entry.get()

        try:
            value = int(value)
        except:
            pass

        new_config[key] = value

    save_config(new_config)

    status_label.configure(
        text="CONFIG SAVED SUCCESSFULLY"
    )

# ==========================================
# START BOT
# ==========================================

bot_process = None

def start_bot():

    global bot_process

    if bot_process is not None:
        status_label.configure(text="BOT ALREADY RUNNING")
        return

    def run():

        global bot_process

        try:

            python_exe = sys.executable

            main_script = os.path.join(BASE_DIR, "main.py")

            status_label.configure(
                text="BOT RUNNING..."
            )

            bot_process = subprocess.Popen(
                [python_exe, main_script],
                cwd=BASE_DIR
            )

            bot_process.wait()

        except Exception as e:

            status_label.configure(
                text=f"ERROR: {str(e)}"
            )

        finally:

            bot_process = None

            status_label.configure(
                text="BOT STOPPED"
            )

    threading.Thread(target=run, daemon=True).start()

# ==========================================
# STOP BOT
# ==========================================

def stop_bot():

    global bot_process

    if bot_process is not None:

        bot_process.terminate()
        bot_process = None

        status_label.configure(
            text="BOT STOPPED"
        )

    else:

        status_label.configure(
            text="NO BOT RUNNING"
        )

# ==========================================
# BUTTON FRAME
# ==========================================

button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=20)

save_button = ctk.CTkButton(
    button_frame,
    text="SAVE CONFIG",
    width=180,
    height=45,
    command=save_settings
)

save_button.grid(row=0, column=0, padx=10)

start_button = ctk.CTkButton(
    button_frame,
    text="START BOT",
    width=180,
    height=45,
    command=start_bot
)

start_button.grid(row=0, column=1, padx=10)

stop_button = ctk.CTkButton(
    button_frame,
    text="STOP BOT",
    width=180,
    height=45,
    fg_color="red",
    hover_color="#aa0000",
    command=stop_bot
)

stop_button.grid(row=0, column=2, padx=10)

# ==========================================
# FOOTER
# ==========================================

footer = ctk.CTkLabel(
    app,
    text="Made with Python + CustomTkinter",
    font=("Arial", 12)
)

footer.pack(side="bottom", pady=10)

# ==========================================
# RUN APP
# ==========================================

app.mainloop()