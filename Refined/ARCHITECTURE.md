# Architecture Documentation - CoC Bot Refined

Technical architecture and design patterns used in the refactored bot.

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **DRY (Don't Repeat Yourself)**: Shared functionality in utilities
3. **Error Handling**: Comprehensive error handling with logging
4. **Configuration as Code**: All constants in dedicated modules
5. **Modularity**: Independent, testable components
6. **Human-Like Behavior**: Randomized delays and patterns

## Module Dependency Graph

```
main.py
  ↓
core/orchestrator.py (Main Loop + Watchdog)
  ├─→ game_actions/navigation.py (go_to_base)
  ├─→ game_actions/scouting.py (evaluate_base)
  ├─→ game_actions/combat.py (deploy_troops)
  │    └─→ tactics/strategy.py (execute_full_army_attack)
  │         ├─→ tactics/troop_selection.py (select_troop)
  │         ├─→ tactics/troop_planning.py (calculate_bunches)
  │         └─→ tactics/deployment.py (deploy_swarm)
  │              ├─→ tactics/base_analysis.py (get_safe_spam_points)
  │              └─→ utils/adb_connector.py (execute shell commands)
  ├─→ game_actions/cleanup.py (return_home)
  ├─→ game_actions/storage.py (check_home_loot)
  └─→ core/recovery.py (rescue_bot)

All modules depend on:
  - utils/logger.py (Logging)
  - utils/adb_connector.py (Device control)
  - utils/vision.py (Image recognition)
  - config/constants.py (Configuration)
  - config/settings.py (Config loading)
```

## Data Flow

### Attack Cycle Flow

```
1. Navigate to Base
   └─→ go_to_base() - Click through UI to find a base
       └─→ Waits for clouds to clear

2. Scout Base
   └─→ evaluate_base() - Read loot values via OCR
       ├─→ Returns (should_attack, gold, elixir)
       └─→ If trash: Click Next and repeat
           If good: Proceed to attack

3. Execute Attack
   └─→ deploy_troops(gold, elixir)
       ├─→ Wait for base to stabilize
       └─→ execute_full_army_attack()
           ├─→ Scan base for tactical points (base_analysis.py)
           ├─→ For each unit in army:
           │   ├─→ select_troop() - Tap troop slot
           │   ├─→ calculate_bunches() - Plan deployment strategy
           │   └─→ deploy_swarm() - Deploy to base
           │       ├─→ Choose deployment side/strategy
           │       ├─→ Calculate drop coordinates
           │       └─→ Execute ADB commands
           └─→ Monitor battle until completion/timeout

4. Return Home
   └─→ return_home()
       ├─→ Click surrender/end battle
       ├─→ Confirm popup
       ├─→ Click return home
       └─→ Wait for home to load

5. Check Storage
   └─→ check_home_loot()
       ├─→ Read gold/elixir via OCR
       └─→ Log percentages and alert if full
```

## Key Components

### 1. Logger (utils/logger.py)

**Purpose**: Structured logging with file and console output

**Features**:
- Color-coded console output
- File logging with timestamps
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Automatic log rotation by date

**Usage**:
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Operation started")
logger.error("Something failed")
```

### 2. ADB Connector (utils/adb_connector.py)

**Purpose**: Manage Android device connection and control

**Features**:
- Connection pooling (single device instance)
- Helper functions for tap, swipe, screenshot
- App restart functionality
- Error handling for disconnections

**Key Functions**:
- `connect_device()` - Establish ADB connection
- `get_device()` - Get current device instance
- `take_screenshot()` - Capture device screen
- `execute_shell_command()` - Run ADB commands
- `tap_screen()` - Send tap event
- `swipe_screen()` - Send swipe event
- `restart_app()` - Force stop and restart app

### 3. Vision Module (utils/vision.py)

**Purpose**: Image recognition, template matching, and OCR

**Features**:
- Template caching to avoid reloading images
- Robust error handling for OCR failures
- Support for region-based matching
- Multi-template matching for efficiency

**Key Functions**:
- `find_and_click()` - Template match and click
- `find_multiple_templates()` - Match multiple templates at once
- `read_loot()` - OCR gold/elixir values
- `read_damage()` - OCR battle damage
- `save_debug_screenshot()` - Visual debugging

### 4. Tactics Module (tactics/)

**Orchestration Flow**:
```
strategy.execute_full_army_attack()
  ├─→ base_analysis.get_safe_spam_points() - Scan base perimeter
  ├─→ For each unit:
  │   ├─→ troop_selection.select_troop() - Click troop slot
  │   ├─→ troop_planning.calculate_bunches() - Plan deployment
  │   └─→ deployment.deploy_swarm() - Execute deployment
  └─→ Return success status
```

### 5. Orchestrator (core/orchestrator.py)

**Purpose**: Main bot loop and safety mechanisms

**Features**:
- Infinite attack loop with statistics
- Watchdog timer (5-minute timeout)
- Anti-detection rest periods
- Cycle counting and statistics

**Watchdog Mechanism**:
```
Every 10 seconds:
  if (current_time - last_action_time) > 300 seconds:
    trigger_recovery()
```

## Configuration Management

### Constants (config/constants.py)

All magic numbers organized by category:

```python
# Timing
HUMAN_REACTION_TIME_MIN = 1.8
CLOUD_LOAD_TIME_MAX = 8.0

# Deployment
HOLD_TIME_PER_TROOP = 40
SPELL_PENETRATION_MIN = 0.55

# Screen Regions
GOLD_REGION = (125, 160, 75, 250)

# OCR Settings
OCR_PSM_MODE_LINE = 7
```

### Settings Loader (config/settings.py)

```python
config = load_config()  # Load config.json
validate_config(config)  # Validate required keys
initialize_constants_from_config(config)  # Update runtime constants
```

## Error Handling Strategy

### Three-Level Error Handling

1. **Function Level**: Try-except with logging
   ```python
   try:
       # operation
   except Exception as e:
       logger.error(f"Failed: {e}")
       return False
   ```

2. **Module Level**: Fallback operations
   ```python
   if not find_and_click("target.png"):
       logger.warning("Click failed, retrying...")
       # Retry logic
   ```

3. **Global Level**: Watchdog recovery
   ```python
   if time_since_last_action > WATCHDOG_TIMEOUT:
       rescue_bot()  # App restart + script reboot
   ```

## Performance Optimizations

### 1. Template Caching

**Problem**: Loading image files is slow
**Solution**: Cache templates in memory

```python
_TEMPLATE_CACHE = {}

def _load_template(image_name):
    if image_name not in _TEMPLATE_CACHE:
        _TEMPLATE_CACHE[image_name] = cv2.imread(path)
    return _TEMPLATE_CACHE[image_name]
```

### 2. Region-Based Matching

**Problem**: Matching entire screen is slow
**Solution**: Crop to relevant region first

```python
def find_and_click_in_region(image_name, region):
    y1, y2, x1, x2 = region
    cropped = screen[y1:y2, x1:x2]
    # Match only in region
```

### 3. Multi-Template Matching

**Problem**: Checking buttons sequentially is slow
**Solution**: Match all templates once, return best

```python
def find_multiple_templates(template_names, screen):
    best_match = None
    best_score = 0
    
    for name in template_names:
        # Match once, keep best
        if score > best_score:
            best_match = name
    
    return best_match
```

### 4. Debug Mode Toggle

**Problem**: Debug file I/O slows down bot
**Solution**: Make debug mode optional

```python
if DEBUG_MODE:
    cv2.imwrite(debug_file, image)  # Only write when needed
```

## Anti-Detection Features

1. **Randomized Delays**
   - All waits use `random.uniform()` instead of fixed `time.sleep()`
   - Prevents detection of bot's predictable timing

2. **Coordinate Randomization**
   - Clicks offset by ±2 pixels randomly
   - Avoids clicking same pixel repeatedly

3. **Deployment Randomization**
   - Troops split into random bunch sizes
   - Deployment order shuffled
   - Different sides chosen randomly

4. **Rest Periods**
   - Bot rests after N base skips (randomized)
   - Rest duration varies (55-85 seconds)
   - Mimics human taking breaks

5. **Human-Like Reactions**
   - 1.8-3.5 second reaction time before acting
   - Varied UI transition delays
   - Randomized cloud loading expectations

## Testing and Debugging

### Debug Output Files

- `logs/bot_YYYY-MM-DD.log` - Complete execution log
- `img/debug_screenshot.png` - Last screenshot with regions marked
- `img/tactical_map.png` - Deployment points visualization

### Calibration Tools

```bash
# Calibrate UI regions
python -m admin.calibration calibrate

# Test template matching
python -m admin.calibration test

# Set up army
python -m admin.army_setup
```

## Extension Points

### Adding New Game Actions

1. Create file in `game_actions/`
2. Implement action function with proper logging
3. Import and call from orchestrator

Example:
```python
# game_actions/new_action.py
def do_something():
    logger.info("Starting action...")
    # Implementation
    return success
```

### Adding New Tactics

1. Create helper in `tactics/`
2. Call from `strategy.py`
3. Update `deployment.py` if affecting deployment

### Adding Configuration Options

1. Add to `config/constants.py`
2. Update `config/settings.py` to load from JSON
3. Use throughout codebase

## Future Improvements

1. **Unit Tests**: Add pytest tests for utilities
2. **Config Validation**: JSON schema validation
3. **Web Dashboard**: Monitor bot from browser
4. **Advanced Logging**: Sentry integration for error tracking
5. **Feature Flags**: Enable/disable features at runtime
6. **Performance Metrics**: Track cycle times and success rates

---

**Version**: 2.0 (Refined)  
**Last Updated**: 2026-06-04
