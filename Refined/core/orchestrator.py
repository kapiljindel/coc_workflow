"""
Orchestrator Module
Manages the main attack loop and watchdog safety timer
"""

import time
import threading
import random
from typing import Optional

from utils.logger import get_logger
from config.constants import (
    WATCHDOG_CHECK_INTERVAL,
    WATCHDOG_TIMEOUT,
    REST_BREAK_MIN,
    REST_BREAK_MAX,
    SKIP_BEFORE_REST_MIN,
    SKIP_BEFORE_REST_MAX,
)
from game_actions.navigation import go_to_base
from game_actions.scouting import evaluate_base
from game_actions.combat import deploy_troops
from game_actions.cleanup import return_home
from game_actions.storage import check_home_loot, get_loot_report
from .recovery import rescue_bot

logger = get_logger(__name__)

class BotOrchestrator:
    """Orchestrates the bot's main attack loop"""
    
    def __init__(self):
        self.last_action_time = time.time()
        self.cycle_count = 0
        self.attack_count = 0
        self.is_running = True
        self.watchdog_thread = None
    
    def start_watchdog(self):
        """Start the watchdog safety timer"""
        self.watchdog_thread = threading.Thread(target=self._watchdog_monitor, daemon=True)
        self.watchdog_thread.start()
        logger.info("✓ Watchdog timer started (5 minute timeout)")
    
    def _watchdog_monitor(self):
        """
        Monitor bot for stuck states
        If no action occurs for 5 minutes, trigger recovery
        """
        while self.is_running:
            time.sleep(WATCHDOG_CHECK_INTERVAL)
            
            elapsed = time.time() - self.last_action_time
            if elapsed > WATCHDOG_TIMEOUT:
                logger.error(f"🚨 WATCHDOG TIMEOUT ({int(elapsed)}s)! Bot appears stuck!")
                rescue_bot()
                self.last_action_time = time.time()
    
    def _rest_countdown(self, seconds: int):
        """Display countdown during rest period"""
        logger.info(f"\n💤 Cooling down to avoid detection...")
        
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            timer = f"{mins:02d}:{secs:02d}"
            logger.info(f"   Resuming in {timer}...", end="\r")
            
            time.sleep(1)
            seconds -= 1
        
        logger.info(f"\n✓ Break complete. Resuming operations!")
    
    def run_attack_cycle(self) -> bool:
        """
        Run a single attack cycle:
        1. Navigate to base
        2. Scout for loot
        3. Execute attack if profitable
        4. Return home and check storage
        
        Returns:
            True if attack completed, False if rested
        """
        try:
            self.last_action_time = time.time()
            
            # Navigate to base
            if not go_to_base():
                logger.warning("Start sequence failed, triggering recovery...")
                rescue_bot()
                return False
            
            # Scout phase
            next_counter = 0
            break_threshold = random.randint(SKIP_BEFORE_REST_MIN, SKIP_BEFORE_REST_MAX)
            
            while True:
                # Anti-detection: rest after skipping N bases
                if next_counter >= break_threshold:
                    logger.info(f"\n🛡️  Anti-Detection: Resting after {next_counter} skips")
                    
                    return_home()
                    rest_time = random.randint(REST_BREAK_MIN, REST_BREAK_MAX)
                    
                    self.last_action_time = time.time() + rest_time
                    self._rest_countdown(rest_time)
                    
                    return False  # Rested, not attacked
                
                # Evaluate base
                should_attack, gold, elixir = evaluate_base()
                
                if should_attack:
                    logger.info(f"\n🎯 JACKPOT! Starting Attack")
                    logger.info(f"   Resources: Gold {gold:,} | Elixir {elixir:,}")
                    
                    # Execute attack
                    deploy_troops(gold, elixir)
                    self.attack_count += 1
                    
                    break
                else:
                    next_counter += 1
                    logger.info(f"   Skipped base #{next_counter}")
            
            # Return home
            return_home()
            
            # Check storage
            loot_report = get_loot_report()
            logger.info(f"📦 {loot_report}")
            
            return True  # Attack completed
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            return False
    
    def run_forever(self):
        """Run the attack loop indefinitely"""
        logger.info("\n" + "=" * 60)
        logger.info("🤖 CoC BOT - STARTING")
        logger.info("=" * 60 + "\n")
        
        self.start_watchdog()
        
        try:
            while self.is_running:
                self.run_attack_cycle()
                self.cycle_count += 1
                
                logger.info("\n" + "-" * 60)
                logger.info(f"📊 Stats - Cycles: {self.cycle_count} | Attacks: {self.attack_count}")
                logger.info("-" * 60 + "\n")
                
                time.sleep(3)  # Brief pause before next cycle
        
        except KeyboardInterrupt:
            logger.info("\n⚠️  Bot interrupted by user")
        except Exception as e:
            logger.error(f"Fatal error: {e}")
        finally:
            self.is_running = False
            logger.info("\n🛑 Bot stopped")
