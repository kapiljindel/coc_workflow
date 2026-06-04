# CoC Bot - File Documentation

This is a **Clash of Clans automation bot** that automatically scouts bases, evaluates loot, and executes attacks. The bot runs on an Android device via ADB (Android Debug Bridge) and uses image recognition (OpenCV + Tesseract OCR) to detect UI elements and loot values.

---

## 📋 Core Execution Flow

```
main.py (Entry Point)
  ↓
start.py (Navigate to attack)
  ↓
loot_checker.py (Evaluate base loot)
  ↓
attack.py → tactics.py (Execute troop deployment)
  ↓
attack_end.py (Return home & collect loot)
  ↓
[Loop with 5-minute watchdog safety]
```

---

## 📁 File Descriptions

### **Core Modules (Main Execution)**

#### [main.py](main.py)
- **Purpose**: Main entry point and orchestrator of the entire bot
- **Key Functions**:
  - Initializes a **watchdog thread** that monitors for stuck states (5-minute timeout)
  - Runs the main attack loop: start → scout → attack → end → rest
  - Manages rest periods between attacks to avoid detection
  - Tracks statistics (cycle count, attack count)
  - Handles errors and triggers recovery if the start sequence fails
- **Dependencies**: start, loot_checker, attack, attack_end, cg_storage_checker, recovery, config

#### [start.py](start.py)
- **Purpose**: Navigates the game UI to find and load a base to attack
- **Key Functions**:
  - `go_to_base()`: Clicks through the menu sequence to reach a base
    1. Opens the Map (main_attack.png)
    2. Clicks "Find Match" button
    3. Clicks "Attack" button (single player)
    4. Waits for clouds to clear and base to load (5.5-8 seconds)
  - Returns `True` on success, `False` on timeout (15+ attempts)
- **Timing**: Uses randomized delays between clicks to mimic human behavior

#### [loot_checker.py](loot_checker.py)
- **Purpose**: Evaluates if a loaded base has enough resources to attack
- **Key Functions**:
  - `evaluate_base()`: 
    - Waits 1.8-3.5 seconds (human reaction time)
    - Takes a screenshot and reads loot values via OCR
    - Compares gold/elixir against `MINIMUM_GOLD` and `MINIMUM_ELIXIR` thresholds
    - Returns `(True, gold, elixir)` if base is worth attacking
    - Clicks "Next" if trash base, waits 5.5-8.5 seconds for clouds
- **Dependencies**: config.read_loot(), config.find_and_click()

#### [attack.py](attack.py)
- **Purpose**: Orchestrates the attack phase after troops are deployed
- **Key Functions**:
  - `deploy_troops(starting_gold, starting_elixir)`:
    - Sets a random time limit for the attack (90-120 seconds)
    - Waits for the base to stabilize (clouds to clear)
    - Calls `tactics.execute_full_army_attack()` to deploy troops
    - Monitors the attack in real-time until time limit is reached
    - Returns when attack should end
- **Features**: Fast telemetry monitoring removed for optimization

#### [tactics.py](tactics.py)
- **Purpose**: Executes the actual battle strategy and troop deployment
- **Key Functions**:
  - `execute_full_army_attack(army_composition)`:
    - Scans the base geometry to find deployment points
    - Randomly chooses one side (Top-Left, Top-Right, Bottom-Right, Bottom-Left)
    - Iterates through army composition (troops → heroes → spells)
    - For each unit: selects the troop and deploys swarms
    - Returns `True` if all troops deployed successfully
- **Dependencies**: select_troop, troop_calculator, deploy_swarm, base_scanner

#### [attack_end.py](attack_end.py)
- **Purpose**: Cleans up after battle and returns to home village
- **Key Functions**:
  - `return_home()`:
    1. Clicks "Surrender" or "End Battle"
    2. Confirms popup with "Okay"
    3. Clicks "Return Home"
    4. Waits for home village to fully load (3.5-5.5 seconds)
    5. Deletes debug screenshot files (calibration, gold, elixir)
- **Timing**: All clicks use randomized intervals to avoid detection

---

### **Troop Deployment Modules**

#### [select_troop.py](select_troop.py)
- **Purpose**: Selects a specific troop from the army bar
- **Key Functions**:
  - `select_troop(troop_name, slot_name)`: 
    - Taps on the specified slot in the army bar
    - Uses randomized pixel selection within the slot region to avoid pixel-perfect patterns
    - Returns `True` on success
- **Dependencies**: config.ARMY_SLOTS, device shell commands

#### [deploy_swarm.py](deploy_swarm.py)
- **Purpose**: Deploys groups of troops onto the base
- **Key Functions**:
  - `deploy_swarm(troop_name, category, bunches, all_side_points, panic_points, chosen_side_name)`:
    - Reads deployment strategy from config.json (`single_side` or `all_sides`)
    - Drops troops in groups (bunches) across chosen points
    - For single_side: drops all troops on one side
    - For all_sides: distributes troops across all sides
    - Includes failsafe panic points if standard points don't work
- **Dependencies**: base_scanner (side points), config.find_and_click()

#### [base_scanner.py](base_scanner.py)
- **Purpose**: Identifies safe deployment zones on enemy bases
- **Key Functions**:
  - `get_safe_spam_points(screen_bytes)`:
    - Analyzes base screenshot to find perimeter points
    - Defines 4 independent lines (Top-Left, Top-Right, Bottom-Right, Bottom-Left)
    - Generates 12 clickable points along each line
    - Generates panic points for failsafe deployment
- **Configuration**: Uses hardcoded coordinates from Tkinter Base Scanner tool
  - LINE_TL: (164, 420) → (665, 61)
  - LINE_TR: (978, 78) → (1419, 400)
  - LINE_BR: (1070, 711) → (1437, 422)
  - LINE_BL: (129, 432) → (495, 700)

#### [troop_calculator.py](troop_calculator.py)
- **Purpose**: Breaks large troop counts into manageable deployment groups
- **Key Functions**:
  - `calculate_bunches(count)`: Splits troop count into optimal bunches (groups to deploy at once)
  - Prevents deploying too many troops at once (game limit)
  - Ensures spread-out deployment for better targeting

---

### **Configuration & Utilities**

#### [config.py](config.py)
- **Purpose**: Central configuration and utility functions
- **Key Components**:
  - **ADB Connection**: `device` object for Android shell commands
  - **Config Loading**: `load_config()` reads from config.json
  - **Constants**:
    - `MINIMUM_GOLD`, `MINIMUM_ELIXIR`: Loot thresholds
    - `TOTAL_TROOPS`: Army unit count
    - `MAX_GOLD`, `MAX_ELIXIR`: Storage capacity limits
    - `IS_UPGRADE_WALL`: Toggle for wall upgrades
    - `MY_ARMY`: Loaded army composition from config.json
    - `ARMY_SLOTS`: Slot coordinates for troop selection
  - **Utility Functions**:
    - `find_and_click(image_name)`: Template matching & clicking
    - `read_loot()`: OCR-based resource detection
    - `get_current_screen()`: Captures device screenshot
    - `save_debug_screenshot()`: Saves cropped resource regions
    - `add_log(log_type, message)`: Writes to log files
  - **Image Regions**: HOME_GOLD_REGION, HOME_ELIXIR_REGION for OCR

#### [config.json](config.json)
- **Purpose**: Runtime configuration file
- **Key Settings**:
  - `ADB_PORT`: Android device connection port (default 5555)
  - `MINIMUM_GOLD`, `MINIMUM_ELIXIR`: Raid thresholds
  - `TOTAL_TROOPS`: Number of troops to deploy per attack
  - `MY_ARMY`: Array of troop objects with name, count, slot
  - `deploy_strategy`: "single_side" or "all_sides" deployment
  - `IS_UPGRADE_WALL`: Whether to auto-upgrade walls
  - Resource limits and other settings

#### [main_config.py](main_config.py)
- **Purpose**: Alternative or legacy configuration module
- **Status**: May be deprecated in favor of config.py + config.json

---

### **Utility & Maintenance Modules**

#### [recovery.py](recovery.py)
- **Purpose**: Emergency recovery for stuck bot states
- **Key Functions**:
  - `rescue_bot()`:
    - Triggered by watchdog when bot inactive for 5+ minutes
    - Force stops Clash of Clans app via ADB
    - Restarts the app with 20-second boot time
    - Reboots the entire Python script using `os.execl()` for full sync
    - Logs the recovery event
- **Purpose**: Prevents infinite hangs and ensures bot resilience

#### [upgrade.py](upgrade.py)
- **Purpose**: Auto-upgrade walls when storage is full
- **Key Functions**:
  - `find_and_click_lowest_cost_wall()`: Finds and upgrades cheapest available wall
- **Triggered By**: When home village loot reaches MAX_GOLD or MAX_ELIXIR thresholds

#### [cg_storage_checker.py](cg_storage_checker.py)
- **Purpose**: Monitors home village storage and sends Telegram notifications
- **Key Components**:
  - `check_home_loot()`: Reads home village gold/elixir via OCR
  - **Telegram Integration**:
    - BOT_TOKEN: "7706951596:AAGg9LF6TV3csG4AW6Q9qu7hmhZp67wHhpQ"
    - CHAT_ID: "#" (configured separately)
  - Notifies when storage is full or special events occur
- **Dependencies**: Telegram API, device screencaps

#### [error.py](error.py)
- **Purpose**: Error handling and logging module
- **Status**: May contain custom exception classes or error handlers

#### [ui.py](ui.py)
- **Purpose**: User interface module (possibly legacy)
- **Status**: Likely contains earlier UI implementations

#### [army_builder.py](army_builder.py)
- **Purpose**: Interactive setup utility for configuring army loadout
- **Key Functions**:
  - `setup_army_loadout()`: Interactive CLI that prompts user to:
    1. Specify number of troop card types
    2. Name each troop and count
    3. Select active heroes (King, Queen, Warden, RC)
    4. Specify spell cards
    5. Maps all units to slots sequentially
  - Returns formatted army array for config.json
- **Usage**: Run standalone to configure MY_ARMY initially

---

### **Logging & Data Files**

#### [data.json](data.json)
- **Purpose**: Persistent data storage for bot state and statistics
- **Contains**: Previous attack logs, loot records, base visit history

#### [README.md](README.md)
- **Purpose**: Documentation and setup instructions
- **Contents**: Installation, ADB setup, configuration guide, usage instructions

#### [logs/ Directory](logs/)
- **Purpose**: Runtime logs organized by date
- **Files**:
  - `YYYY-MM-DD_attack.txt`: Attack execution logs
  - `YYYY-MM-DD_errors.txt`: Error and exception logs
  - `YYYY-MM-DD_resources.txt`: Loot detection records
  - `YYYY-MM-DD_buttons.txt`: Button click logs
  - `log`: Main combined log file

---

### **Asset Files**

#### [assets/ Directory](assets/)
- **Contains**: Game screenshot templates used for image recognition
- `dragon.png1`: Dragon troop template image
- Other templates: main_attack.png, find_match.png, single_player_attack.png, etc.

#### [img/ Directory](img/)
- **Purpose**: Runtime image storage
- **Contains**: 
  - Screenshots captured during attacks (debug_gold.png, debug_elixir.png)
  - Calibration images
  - Cleaned up after each attack cycle

---

### **Version Control & Legacy**

#### [version/ Directory](version/)
- **Purpose**: Version history and iteration tracking
- **Structure**:
  - `v1/`: Original bot (coc_bot.py, v2.py, v3.py, v4.py, v5.py)
  - `v2/`: Second iteration (attack_end.py, attack.py, config.py, etc.)
  - `v3/`, `v4/`, `v5/`: Subsequent iterations
- **Usage**: Reference and rollback capability

#### [worker/ Directory](worker/)
- **Purpose**: Production-ready working copy of the bot
- **Contents**: Copies of all core modules from main directory
- **Status**: Staging area for deployed bot instances

---

### **Legacy/Inactive Files**

#### [auto.py](auto.py)
- **Status**: Likely deprecated automation module

#### [new.py](new.py)
- **Purpose**: Experimental new features (status unclear)

#### [tactics-old.py](tactics-old.py)
- **Purpose**: Previous tactics implementation
- **Status**: Kept for reference, replaced by tactics.py

#### [start-b.py](start-b.py)
- **Purpose**: Alternative start sequence (likely backup)

#### [base_scanner copy.py](base_scanner%20copy.py)
- **Purpose**: Backup of base_scanner.py

#### [deploy_swarm copy.py](deploy_swarm%20copy.py)
- **Purpose**: Backup of deploy_swarm.py

#### [storage_check1.py](storage_check1.py)
- **Purpose**: Earlier version of cg_storage_checker.py

---

## 🛠️ Key Technologies

- **ADB (Android Debug Bridge)**: Communicates with Android device
- **OpenCV (cv2)**: Image processing and template matching
- **Tesseract OCR**: Optical character recognition for loot values
- **ppadb**: Pure Python ADB client
- **Telegram API**: Push notifications
- **Threading**: Watchdog monitoring in background

---

## 🔄 Bot Workflow Summary

1. **Start** → Navigate to attack screen, load a random base
2. **Scout** → Evaluate loot via OCR, decide if profitable
3. **Attack** → Deploy troops in strategic waves
4. **End** → Return home, surrender, collect loot
5. **Rest** → Cool down period (randomized) to avoid detection
6. **Watchdog** → Monitor activity every 10 seconds, recover if stuck >5 minutes
7. **Loop** → Repeat indefinitely until manually stopped

---

## 📊 Statistics & Monitoring

- **Cycle Count**: Tracks number of complete attack loops
- **Attack Count**: Tracks successful attacks
- **Logs**: Detailed logs per day (attacks, errors, resources)
- **Telegram**: Optional notifications for storage full, errors, milestones

