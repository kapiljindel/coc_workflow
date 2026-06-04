# CoC Bot - Refined Edition

A professionally refactored **Clash of Clans automation bot** with clean architecture, proper error handling, and optimized code structure.

## 📁 Project Structure

```
Refined/
├── core/                    # Main bot logic and orchestration
│   ├── main.py             # Entry point
│   ├── orchestrator.py     # Main loop and watchdog
│   └── recovery.py         # Crash recovery
│
├── game_actions/           # Individual game actions
│   ├── navigation.py       # Navigate to bases
│   ├── scouting.py         # Evaluate base loot
│   ├── combat.py           # Execute attacks
│   ├── cleanup.py          # Return home
│   └── storage.py          # Check home storage
│
├── tactics/                # Combat strategy and deployment
│   ├── strategy.py         # Overall battle tactics
│   ├── deployment.py       # Troop deployment (refactored)
│   ├── troop_selection.py  # Select troops
│   ├── troop_planning.py   # Calculate deployment bunches
│   └── base_analysis.py    # Scan base for tactical points
│
├── utils/                  # Utility and helper modules
│   ├── logger.py           # Structured logging
│   ├── adb_connector.py    # Android Device Bridge
│   ├── vision.py           # Image recognition and OCR
│   └── __init__.py
│
├── config/                 # Configuration management
│   ├── constants.py        # All constants and magic numbers
│   ├── settings.py         # Config file loader
│   └── __init__.py
│
├── admin/                  # Setup and administration tools
│   ├── army_setup.py       # Interactive army configuration
│   ├── calibration.py      # UI calibration tools
│   └── __init__.py
│
├── assets/                 # Game UI template images
├── logs/                   # Bot logs (auto-generated)
├── img/                    # Debug screenshots (auto-generated)
│
├── main.py                 # Entry point (copy to parent)
├── config.json             # Configuration (copy from parent)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── SETUP.md               # Installation and setup guide
└── ARCHITECTURE.md        # Detailed architecture docs
```

## 🚀 Quick Start

### 1. Setup

```bash
# Copy the Refined folder to your working directory
# Install dependencies
pip install -r requirements.txt

# Configure your bot
python -m admin.army_setup  # Interactive army setup

# Edit config.json with your settings
```

### 2. Run the Bot

```bash
python main.py
```

## 📋 Module Documentation

### Core Modules (`core/`)

- **main.py**: Entry point that initializes logging, connects to device, and starts the orchestrator
- **orchestrator.py**: Main attack loop with watchdog timer (5-minute timeout)
- **recovery.py**: Emergency recovery procedures when bot gets stuck

### Game Actions (`game_actions/`)

- **navigation.py**: Navigates game UI to find and load a base
- **scouting.py**: Evaluates base loot and determines if it's worth attacking
- **combat.py**: Orchestrates the attack phase (calls tactics)
- **cleanup.py**: Returns home after battle and cleans up
- **storage.py**: Checks home village storage levels

### Tactics (`tactics/`)

- **strategy.py**: Orchestrates complete army deployment
- **deployment.py**: Deploys individual troops/spells to base (refactored from deploy_swarm.py)
- **troop_selection.py**: Selects specific troops from army bar
- **troop_planning.py**: Calculates deployment bunches for unpredictable patterns
- **base_analysis.py**: Scans base for tactical deployment points

### Utilities (`utils/`)

- **logger.py**: Structured logging with file and console output
- **adb_connector.py**: Android Debug Bridge connection management
- **vision.py**: Image recognition, template matching, OCR (refactored from config.py)

### Configuration (`config/`)

- **constants.py**: ALL magic numbers and configuration values
- **settings.py**: Loads and validates config.json

### Administration (`admin/`)

- **army_setup.py**: Interactive tool to configure your army
- **calibration.py**: UI calibration and testing tools

## 🔧 Configuration

Edit `config.json` to customize:

```json
{
    "ADB_PORT": 5555,
    "MINIMUM_GOLD": 400000,
    "MINIMUM_ELIXIR": 400000,
    "MAX_GOLD": 9250000,
    "MAX_ELIXIR": 9250000,
    "TOTAL_TROOPS": 120,
    "IS_UPGRADE_WALL": true,
    "deploy_strategy": "single_side",
    "MY_ARMY": [...]
}
```

## 📊 Key Improvements Over Original

| Issue | Original | Refined |
|-------|----------|---------|
| **Code Organization** | Mixed concerns, files scattered | Proper module structure with clear separation |
| **Duplicate Code** | Functions defined twice in config.py | Single definition per function |
| **File Size** | config.py: 400+ lines | Split into vision.py, adb_connector.py, logger.py |
| **Magic Numbers** | Scattered throughout code | All in constants.py with meaningful names |
| **Dead Code** | Commented-out code blocks | Completely removed |
| **Error Handling** | Silent failures | Proper error handling and logging |
| **Logging** | Manual category tracking | Python logging module with levels |
| **Documentation** | Minimal | Comprehensive docstrings and guides |
| **Maintainability** | Hard to modify | Easy to add features and fix bugs |

## 🎯 Usage Examples

### Run the Bot

```bash
python main.py
```

### Setup Army Interactively

```bash
python -m admin.army_setup
```

### Calibrate UI Coordinates

```bash
python -m admin.calibration calibrate
```

### Test Template Matching

```bash
python -m admin.calibration test
```

## 📝 Logging

Logs are automatically saved to `logs/bot_YYYY-MM-DD.log` with three levels:

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages (console + file)
- **WARNING**: Warning messages
- **ERROR**: Error messages (auto-logged on failure)

## 🛡️ Safety Features

- **Watchdog Timer**: 5-minute timeout with automatic recovery if bot stuck
- **Anti-Detection**: Rest periods after N base skips
- **Human-Like Delays**: Randomized click intervals and transition times
- **Error Recovery**: Automatic app restart and bot reboot on crash

## 🔍 Debugging

Enable debug mode to see:
- Screenshot captures with marked UI regions
- Tactical deployment point visualization
- Detailed logging to console and file

Debug images are saved to the `img/` folder.

## ⚙️ Customization

All timing, thresholds, and magic numbers are in `config/constants.py`:

```python
# Timing
HUMAN_REACTION_TIME_MIN = 1.8
ATTACK_DURATION_MIN = 90
ATTACK_DURATION_MAX = 120

# Deployment
HOLD_TIME_PER_TROOP = 40  # milliseconds
SPELL_PENETRATION_MIN = 0.55
SPELL_PENETRATION_MAX = 0.75

# Anti-Detection
REST_BREAK_MIN = 55
REST_BREAK_MAX = 85
```

## 🐛 Troubleshooting

**Bot not connecting to device:**
```bash
# Check ADB connection
adb devices
# Update ADB_PORT in config.json if needed
```

**Template not found errors:**
```bash
# Run calibration to verify images
python -m admin.calibration calibrate
```

**Bot freezing or stuck:**
- Watchdog timer should automatically trigger recovery after 5 minutes
- Check logs for specific error messages
- Verify device is still responsive with ADB

## 📚 Documentation

See detailed documentation:
- [SETUP.md](SETUP.md) - Installation and configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture details

## 📄 License

This bot is provided as-is for educational purposes.

---

**Version**: 2.0 (Refined)  
**Last Updated**: 2026-06-04
