# Setup Guide - CoC Bot Refined

Complete step-by-step setup instructions.

## Prerequisites

- Python 3.7+
- Android device or emulator (BlueStacks, NOX, etc.)
- Android Debug Bridge (ADB)
- Tesseract OCR
- Clash of Clans game installed

## Installation Steps

### 1. Install Python Dependencies

```bash
cd Refined
pip install -r requirements.txt
```

**Key packages:**
- `opencv-python` - Image processing
- `pytesseract` - OCR text recognition
- `ppadb` - Android Debug Bridge
- `numpy` - Array processing

### 2. Set Up ADB Connection

#### Windows with BlueStacks:

```bash
# Locate BlueStacks ADB
cd "C:\Program Files\BlueStacks"
adb connect 127.0.0.1:5555

# Verify connection
adb devices
```

You should see your device listed.

#### Linux:

```bash
sudo apt-get install adb
adb connect <device-ip>:5555
adb devices
```

#### macOS:

```bash
brew install android-platform-tools
adb connect 127.0.0.1:5555
adb devices
```

### 3. Configure Tesseract OCR

Tesseract path is already configured for Windows:
```python
# In config/constants.py
TESSERACT_PATH = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'
```

**For Linux/Mac:**
```bash
# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

Then update `TESSERACT_PATH` in `config/constants.py`:
```python
# Linux
TESSERACT_PATH = '/usr/bin/tesseract'

# macOS
TESSERACT_PATH = '/usr/local/bin/tesseract'
```

### 4. Capture Game Template Images

All game UI template images must be in `assets/` folder:

```
assets/
├── main_attack.png
├── find_match.png
├── single_player_attack.png
├── next_base.png
├── surrender.png
├── end_battle.png
├── okay.png
├── return_home.png
└── ... (more templates)
```

**To capture templates:**
1. Run: `python -m admin.calibration calibrate`
2. Take screenshots of each button in the game
3. Save as PNG in `assets/` folder

### 5. Configure Your Army

Run the interactive setup wizard:

```bash
python -m admin.army_setup
```

This will ask you:
- How many troop cards you have
- Troop names and quantities
- Which heroes are active
- How many spell cards
- Spell names and quantities

Output will be saved to config.json.

### 6. Edit config.json

```json
{
    "ADB_PORT": 5555,
    "MINIMUM_GOLD": 400000,
    "MINIMUM_ELIXIR": 400000,
    "TOTAL_TROOPS": 120,
    "MAX_GOLD": 9250000,
    "MAX_ELIXIR": 9250000,
    "IS_UPGRADE_WALL": false,
    "deploy_strategy": "single_side",
    "MY_ARMY": [
        {
            "name": "dragon",
            "category": "troop",
            "count": 20,
            "slot": "slot_1"
        },
        ...
    ]
}
```

**Key settings:**
- `ADB_PORT`: Port your device connects on (usually 5555)
- `MINIMUM_GOLD/ELIXIR`: Attack threshold values
- `MY_ARMY`: Your troop composition
- `deploy_strategy`: "single_side", "all_sides", or other options

### 7. Calibrate UI Regions

Update these in `config/constants.py` based on your screen resolution:

```python
# Screen Regions (y1, y2, x1, x2) - adjust for your device
GOLD_REGION = (125, 160, 75, 250)
ELIXIR_REGION = (165, 200, 75, 250)
DAMAGE_REGION = (620, 700, 1350, 1580)
```

To find correct regions:
1. Run: `python -m admin.calibration calibrate`
2. Open debug image: `img/debug_screenshot.png`
3. Note the (x, y) coordinates of each UI element
4. Update regions in constants.py

### 8. Test the Setup

```bash
# Calibrate and verify regions
python -m admin.calibration calibrate

# Test template matching
python -m admin.calibration test
```

## Running the Bot

### Start the Bot

```bash
python main.py
```

Expected output:
```
[HH:MM:SS] INFO - coc_bot - ============================================================
[HH:MM:SS] INFO - coc_bot - 🤖 CoC BOT - STARTING
[HH:MM:SS] INFO - coc_bot - ============================================================
[HH:MM:SS] INFO - coc_bot - ✓ Watchdog timer started (5 minute timeout)
[HH:MM:SS] INFO - coc_bot.core.orchestrator - Opening Map...
...
```

### Monitor the Bot

Logs are saved to: `logs/bot_YYYY-MM-DD.log`

Watch for:
- `✓` - Success messages
- `⚠️` - Warnings
- `✗` - Errors
- `🚨` - Critical issues (triggers watchdog recovery)

### Stop the Bot

Press `Ctrl+C` to gracefully stop

## Troubleshooting

### "Could not connect to device"

```bash
# Check ADB is running
adb devices

# Reconnect
adb connect 127.0.0.1:5555

# Verify in config.json
# ADB_PORT should match (usually 5555)
```

### "Template not found" errors

1. Verify template images exist in `assets/`
2. Run calibration: `python -m admin.calibration calibrate`
3. Check that image names match in code

### "Tesseract not found"

Check TESSERACT_PATH in `config/constants.py`:
```bash
# Windows
TESSERACT_PATH = r'D:\path\to\tesseract.exe'

# Linux/Mac
# Test path
which tesseract
# Update TESSERACT_PATH
```

### Bot stuck or freezing

- Watchdog timer should auto-recover after 5 minutes
- Check `logs/` folder for error messages
- Verify device is responsive: `adb shell ping 8.8.8.8`

## Performance Tips

1. **Increase Stability**: Add more cloud wait time in constants.py
2. **Faster Farming**: Reduce `HUMAN_REACTION_TIME_*` values
3. **Better Detection**: Adjust template matching thresholds
4. **Less Detectable**: Increase REST_BREAK times

## Common Issues

| Problem | Solution |
|---------|----------|
| Connection drops | Reconnect ADB: `adb connect 127.0.0.1:5555` |
| Image matching fails | Run calibration and update template images |
| Wrong troop deployed | Check MY_ARMY in config.json and slots |
| App crashes | Watchdog will recover after 5 minutes |
| OCR not reading | Update loot region coordinates |

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Customize timing in `config/constants.py`
- Add more template images for different game states
- Monitor and adjust loot thresholds

---

Need help? Check the logs folder for detailed error messages!
