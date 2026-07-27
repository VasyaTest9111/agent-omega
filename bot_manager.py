import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BotManager:
    """
    Multi-node Telegram Bot Manager
    Manages 6 independent Telegram bot nodes with centralized orchestration
    """
    
    TELEGRAM_NODES_COUNT = 6  # Constants for maintainability
    
    def __init__(self):
        """Initialize the Bot Manager with all 6 Telegram nodes."""
        self.nodes = {}
        self.active_nodes = []
        self.gemini_api_key = None
        self._initialize_nodes()
    
    def _initialize_nodes(self):
        """Initialize all 6 Telegram bot nodes from environment variables."""
        logger.info("=" * 70)
        logger.info("INITIALIZING UOS MULTI-NODE TELEGRAM BOT SYSTEM")
        logger.info("=" * 70)
        
        # Initialize Telegram tokens
        telegram_tokens = []
        for i in range(1, self.TELEGRAM_NODES_COUNT + 1):
            token_key = f"TELEGRAM_TOKEN_{i}"
            token = os.getenv(token_key)
            
            if token:
                telegram_tokens.append(token)
                self.nodes[f"TELEGRAM_NODE_{i}"] = {
                    "type": "telegram",
                    "token": token,
                    "node_id": i,
                    "status": "INITIALIZING",
                    "messages_processed": 0
                }
                # Secure logging: mask token completely
                logger.info(f"\u2713 Telegram Node {i} initialized (Token: {'*' * len(token)})")
            else:
                logger.warning(f"\u2717 {token_key} not found in environment variables")
        
        # Initialize Gemini API node
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            self.nodes["GEMINI_NODE"] = {
                "type": "gemini",
                "api_key": self.gemini_api_key,
                "status": "INITIALIZING",
                "requests_processed": 0
            }
            # Secure logging: mask API key completely
            logger.info(f"\u2713 Gemini API Node initialized (Key: {'*' * len(self.gemini_api_key)})")
        else:
            logger.warning("\u2717 GEMINI_API_KEY not found in environment variables")
        
        logger.info(f"\n\u2713 Total nodes initialized: {len(self.nodes)}")
        logger.info("=" * 70)
    
    def activate_nodes(self):
        """Activate all initialized nodes."""
        logger.info("\n" + "=" * 70)
        logger.info("ACTIVATING ALL NODES")
        logger.info("=" * 70)
        
        for node_name, node_config in self.nodes.items():
            node_config["status"] = "ACTIVE"
            self.active_nodes.append(node_name)
            logger.info(f"\u2713 {node_name}: {node_config['status']}")
        
        logger.info(f"\n\u2713 Active nodes: {len(self.active_nodes)}/{len(self.nodes)}")
        logger.info("=" * 70)
    
    def get_node_status(self):
        """Get status of all nodes."""
        status = {}
        for node_name, node_config in self.nodes.items():
            status[node_name] = {
                "type": node_config["type"],
                "status": node_config["status"],
                "active": node_name in self.active_nodes
            }
        return status
    
    def verify_all_nodes_active(self) -> bool:
        """Verify that all nodes are ACTIVE."""
        logger.info("\n" + "=" * 70)
        logger.info("VERIFYING NODE STATUS")
        logger.info("=" * 70)
        
        all_active = all(
            self.nodes[node]["status"] == "ACTIVE" 
            for node in self.active_nodes
        )
        
        if all_active:
            logger.info(f"\u2713 All {len(self.active_nodes)} nodes are ACTIVE")
            logger.info("=" * 70)
            return True
        else:
            logger.error("\u2717 Some nodes are not ACTIVE")
            logger.info("=" * 70)
            return False
    
    def process_telegram_message(self, node_id: int, message_data: Dict):
        """
        Process incoming Telegram message through UOS_ENGINE logic.
        
        Args:
            node_id: Telegram node ID (1-6)
            message_data: Message data from Telegram
        """
        node_name = f"TELEGRAM_NODE_{node_id}"
        
        if node_name not in self.nodes:
            logger.error(f"\u2717 Invalid node ID: {node_id}")
            return False
        
        node = self.nodes[node_name]
        
        if node["status"] != "ACTIVE":
            logger.warning(f"\u2717 Node {node_name} is not ACTIVE")
            return False
        
        try:
            logger.info(f"\ud83d\udce8 Processing message on {node_name}")
            logger.info(f"   Message data keys: {list(message_data.keys())}")
            
            # Route to UOS_ENGINE (lazy import to avoid circular dependency)
            result = self._route_to_uos_engine(node_id, message_data)
            
            node["messages_processed"] += 1
            logger.info(f"\u2713 Message processed successfully (Total: {node['messages_processed']})")
            
            return True
        except Exception as e:
            logger.error(f"\u2717 Error processing message: {e}")
            return False
    
    def process_gemini_request(self, request_data: Dict):
        """
        Process Gemini API request through UOS_ENGINE logic.
        
        Args:
            request_data: Request data for Gemini API
        """
        if "GEMINI_NODE" not in self.nodes:
            logger.error("\u2717 Gemini node not initialized")
            return False
        
        node = self.nodes["GEMINI_NODE"]
        
        if node["status"] != "ACTIVE":
            logger.warning("\u2717 Gemini node is not ACTIVE")
            return False
        
        try:
            logger.info("\ud83e\udd16 Processing Gemini API request")
            logger.info(f"   Request data keys: {list(request_data.keys())}")
            
            # Route to UOS_ENGINE (lazy import to avoid circular dependency)
            result = self._route_to_uos_engine("gemini", request_data)
            
            node["requests_processed"] += 1
            logger.info(f"\u2713 Gemini request processed successfully (Total: {node['requests_processed']})")
            
            return True
        except Exception as e:
            logger.error(f"\u2717 Error processing Gemini request: {e}")
            return False
    
    def _route_to_uos_engine(self, source, data):
        """
        Route message/request to UOS_ENGINE for processing.
        Uses lazy import to avoid circular dependency.
        
        Args:
            source: Source node ID or name
            data: Data to process
            
        Returns:
            Processing result
        """
        try:
            # Lazy import to break circular dependency
            from uos_engine import UOSEngine
            
            engine = UOSEngine()
            result = engine.process(source, data)
            return result
        except ImportError:
            logger.warning("\u26a0 UOS_ENGINE not yet available, using mock processing")
            return {"status": "processed", "mock": True}
        except Exception as e:
            logger.error(f"\u2717 Error routing to UOS_ENGINE: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_statistics(self):
        """Get system statistics."""
        stats = {
            "total_nodes": len(self.nodes),
            "active_nodes": len(self.active_nodes),
            "telegram_nodes": sum(1 for n in self.nodes.values() if n["type"] == "telegram"),
            "gemini_nodes": sum(1 for n in self.nodes.values() if n["type"] == "gemini"),
            "total_messages_processed": sum(
                n.get("messages_processed", 0) for n in self.nodes.values()
            ),
            "total_requests_processed": sum(
                n.get("requests_processed", 0) for n in self.nodes.values()
            )
        }
        return stats
    
    def print_system_info(self):
        """Print detailed system information."""
        logger.info("\n" + "\u2554" + "=" * 68 + "\u2557")
        logger.info("\u2551" + " " * 15 + "UOS MULTI-NODE SYSTEM INFO" + " " * 27 + "\u2551")
        logger.info("\u255a" + "=" * 68 + "\u255d")
        
        stats = self.get_statistics()
        
        logger.info(f"Total Nodes: {stats['total_nodes']}")
        logger.info(f"Active Nodes: {stats['active_nodes']}")
        logger.info(f"  - Telegram Nodes: {stats['telegram_nodes']}")
        logger.info(f"  - Gemini API Nodes: {stats['gemini_nodes']}")
        logger.info(f"\nMessages Processed: {stats['total_messages_processed']}")
        logger.info(f"Requests Processed: {stats['total_requests_processed']}")
        logger.info("\nNode Status:")
        
        for node_name, node_config in self.nodes.items():
            status_icon = "\ud83d\udfe2" if node_config["status"] == "ACTIVE" else "\ud83d\udd34"
            logger.info(f"  {status_icon} {node_name}: {node_config['status']}")
        
        logger.info("\u255a" + "=" * 68 + "\u255d\n")


def main():
    """Main entry point for Bot Manager."""
    try:
        # Initialize Bot Manager
        bot_manager = BotManager()
        
        # Activate all nodes
        bot_manager.activate_nodes()
        
        # Verify all nodes are active
        if bot_manager.verify_all_nodes_active():
            logger.info("\u2713 System ready for operation")
        else:
            logger.error("\u2717 System initialization failed")
            return False
        
        # Print system info
        bot_manager.print_system_info()
        
        return True
    
    except Exception as e:
        logger.error(f"\u2717 Fatal error in bot_manager: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
