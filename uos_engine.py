import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Fallback SystemState class in case SYSTEM_CONFIG.py is not available
class SystemState:
    """Fallback SystemState class for when SYSTEM_CONFIG.py is not available."""
    def __init__(self):
        self.state = "ACTIVE"
        self.registry = "CORE_INTEGRATION"
        self.operational_mode = "AUTONOMOUS"

    def get_status(self):
        return f"System status: {self.state} | Mode: {self.operational_mode}"


# Try to import from SYSTEM_CONFIG, fall back to local class if not available
try:
    from SYSTEM_CONFIG import SystemState as SystemStateFromConfig
    SystemState = SystemStateFromConfig
except ImportError:
    logger.info("\u26a0 SYSTEM_CONFIG.py not found, using fallback SystemState")


class UOSEngine:
    """
    Universal Operating System Engine
    Central orchestration and processing engine for all UOS subsystems
    """
    
    def __init__(self):
        """Initialize the UOS Engine."""
        try:
            self.system_state = SystemState()
            logger.info(f"\u2713 UOSEngine initialized | {self.system_state.get_status()}")
            
            # Import Bot Manager for multi-node handling (lazy import to avoid circular dependency)
            from bot_manager import BotManager
            self.bot_manager = BotManager()
            
        except Exception as e:
            logger.error(f"\u2717 Failed to initialize UOSEngine: {e}")
            raise
    
    def process(self, source, data):
        """
        Main processing method for UOS Engine.
        
        Args:
            source: Source identifier (telegram node ID or "gemini")
            data: Data to process
            
        Returns:
            Processing result
        """
        try:
            # Verify system state
            if self.system_state.state != "ACTIVE":
                logger.warning(
                    f"\u2717 Cannot process: System state is {self.system_state.state}, expected ACTIVE"
                )
                return {"status": "error", "message": "System not ACTIVE"}
            
            # Route based on source
            if isinstance(source, int):
                # Telegram message from specific node
                return self.bot_manager.process_telegram_message(source, data)
            elif source == "gemini":
                # Gemini API request
                return self.bot_manager.process_gemini_request(data)
            else:
                logger.error(f"\u2717 Unknown source: {source}")
                return {"status": "error", "message": "Unknown source"}
        
        except Exception as e:
            logger.error(f"\u2717 Error processing in UOSEngine: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_system_status(self):
        """Get comprehensive system status."""
        return {
            "uos_state": self.system_state.state,
            "uos_mode": self.system_state.operational_mode,
            "uos_registry": self.system_state.registry,
            "bot_nodes": self.bot_manager.get_node_status(),
            "statistics": self.bot_manager.get_statistics()
        }


def main():
    """Main entry point for UOS Engine."""
    try:
        logger.info("=" * 70)
        logger.info("STARTING UNIVERSAL OPERATING SYSTEM ENGINE")
        logger.info("=" * 70)
        
        # Initialize UOS Engine
        engine = UOSEngine()
        
        # Activate all bot nodes
        engine.bot_manager.activate_nodes()
        
        # Verify all nodes are ACTIVE
        if not engine.bot_manager.verify_all_nodes_active():
            logger.error("\u2717 Node verification failed")
            return False
        
        # Print system information
        engine.bot_manager.print_system_info()
        
        # Get and log system status
        status = engine.get_system_status()
        logger.info("UOS Engine Status:")
        logger.info(f"  State: {status['uos_state']}")
        logger.info(f"  Mode: {status['uos_mode']}")
        logger.info(f"  Registry: {status['uos_registry']}")
        
        logger.info("=" * 70)
        logger.info("\u2713 UOS ENGINE READY FOR OPERATION")
        logger.info("=" * 70)
        
        return True
    
    except Exception as e:
        logger.error(f"\u2717 Fatal error in UOS Engine: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
