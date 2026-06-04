"""
Constants and Configuration Values for CoC Bot
All magic numbers and configuration parameters consolidated here
"""

import os

# ==========================================
# FOLDER PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
LOGS_PATH = os.path.join(BASE_DIR, "logs")
IMG_PATH = os.path.join(BASE_DIR, "img")
CONFIG_FILE = "config.json"

# ==========================================
# TESSERACT OCR PATH
# ==========================================
TESSERACT_PATH = r'D:\coc_bot\platform-tools\Tesseract-OCR\tesseract.exe'

# ==========================================
# TIMING CONSTANTS (in seconds)
# ==========================================
# Human reaction times
HUMAN_REACTION_TIME_MIN = 1.8
HUMAN_REACTION_TIME_MAX = 3.5

# Cloud loading times
CLOUD_LOAD_TIME_MIN = 5.5
CLOUD_LOAD_TIME_MAX = 8.0
CLOUD_LOAD_TIME_EXTENDED_MIN = 5.5
CLOUD_LOAD_TIME_EXTENDED_MAX = 8.5

# Battle timing
ATTACK_DURATION_MIN = 90
ATTACK_DURATION_MAX = 120

# UI transition timing
UI_TRANSITION_MIN = 0.4
UI_TRANSITION_MAX = 0.9

# Stabilization check timing
LOOT_STABILIZATION_CHECK_MIN = 0.4
LOOT_STABILIZATION_CHECK_MAX = 0.7

# Return home timing
RETURN_HOME_MIN = 3.5
RETURN_HOME_MAX = 5.5

# Click timing
CLICK_DELAY_MIN = 0.15
CLICK_DELAY_MAX = 0.45

# Retry timing
RETRY_DELAY_MIN = 0.8
RETRY_DELAY_MAX = 1.3

# Surrender timing
SURRENDER_CONFIRM_MIN = 0.7
SURRENDER_CONFIRM_MAX = 1.2

# Battle summary screen transition
BATTLE_SUMMARY_TRANSITION_MIN = 1.8
BATTLE_SUMMARY_TRANSITION_MAX = 3.2

# Watchdog recovery timing
WATCHDOG_CHECK_INTERVAL = 10  # seconds
WATCHDOG_TIMEOUT = 300  # 5 minutes
APP_BOOT_TIME = 20  # seconds after restart

# ==========================================
# DEPLOYMENT CONSTANTS
# ==========================================
# Troop bundling
MIN_BUNCHES = 4
MAX_BUNCHES = 8

# Troop deployment hold time (milliseconds per troop)
HOLD_TIME_PER_TROOP = 40  # ms

# Troop position randomization
TROOP_POSITION_OFFSET_MIN = -15
TROOP_POSITION_OFFSET_MAX = 15

# Spell deployment
SPELL_PENETRATION_MIN = 0.55
SPELL_PENETRATION_MAX = 0.75
SPELL_OFFSET_MIN = -40
SPELL_OFFSET_MAX = 40

# Hero deployment
HERO_TAP_COUNT_MIN = 2
HERO_TAP_COUNT_MAX = 3

# Cleanup taps
CLEANUP_TAP_COUNT = 2

# Tactical points
TACTICAL_POINTS_PER_SIDE = 12

# ==========================================
# TEMPLATE MATCHING
# ==========================================
TEMPLATE_MATCH_THRESHOLD_HIGH = 0.85
TEMPLATE_MATCH_THRESHOLD_DEFAULT = 0.8
TEMPLATE_MATCH_THRESHOLD_LOW = 0.7
TEMPLATE_MATCH_METHOD = "TM_CCOEFF_NORMED"

# ==========================================
# ANTI-DETECTION
# ==========================================
REST_BREAK_MIN = 55  # seconds
REST_BREAK_MAX = 85  # seconds
SKIP_BEFORE_REST_MIN = 10
SKIP_BEFORE_REST_MAX = 15

# Randomize coordinates
COORDINATE_RANDOMIZATION_MIN = -2
COORDINATE_RANDOMIZATION_MAX = 2

# ==========================================
# SCREEN REGIONS (y1, y2, x1, x2)
# ==========================================
# Loot detection regions
GOLD_REGION = (125, 160, 75, 250)
ELIXIR_REGION = (165, 200, 75, 250)

# Damage tracking
DAMAGE_REGION = (620, 700, 1350, 1580)

# Troop count
TROOP_REGION = (738, 768, 150, 250)

# Home village storage
HOME_GOLD_REGION = (32, 73, 1300, 1510)
HOME_ELIXIR_REGION = (117, 158, 1300, 1510)

# Builder menu
BUILDER_LIST_REGION = (124, 685, 600, 1038)

# ==========================================
# OCR SETTINGS
# ==========================================
OCR_PSM_MODE_LINE = 7  # PSM mode for single line
OCR_PSM_MODE_BLOCK = 6  # PSM mode for block of text
OCR_UPSCALE_FACTOR = 3  # Image upscaling before OCR

# ==========================================
# COLOR DETECTION (for base scanning)
# ==========================================
RED_THRESHOLD_MIN = 110
RED_G_DIFF = 35  # r > g + 35
RED_B_DIFF = 35  # r > b + 35
BASE_BLOB_KERNEL_SIZE = 15
BASE_BLOB_DILATION_ITERATIONS = 2

# ==========================================
# DEBUG & LOGGING
# ==========================================
DEBUG_MODE = True
LOG_LEVEL_CONSOLE = "INFO"
LOG_LEVEL_FILE = "DEBUG"

# ==========================================
# ADB & DEVICE
# ==========================================
ADB_HOST = "127.0.0.1"
ADB_PORT_DEFAULT = 5037
ADB_DEVICE_PORT_DEFAULT = 5555

# ==========================================
# LOOT THRESHOLDS (populated from config.json)
# ==========================================
MINIMUM_GOLD = None  # Set from config.json
MINIMUM_ELIXIR = None  # Set from config.json
MAX_GOLD = None  # Set from config.json
MAX_ELIXIR = None  # Set from config.json
TOTAL_TROOPS = None  # Set from config.json

# ==========================================
# DEPLOYMENT STRATEGY
# ==========================================
STRATEGY_SINGLE_SIDE = "single_side"
STRATEGY_ALL_SIDES = "all_sides"
STRATEGY_CIRCLE = "circle"
STRATEGY_SINGLE_POINT = "single_point"
STRATEGY_RANDOM_SIDE = "random_side"

# ==========================================
# ARMY COMPOSITION (populated from config.json)
# ==========================================
MY_ARMY = None  # Set from config.json
ARMY_SLOTS = None  # Set dynamically from MY_ARMY
