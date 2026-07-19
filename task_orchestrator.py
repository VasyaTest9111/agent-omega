import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import SystemState from SYSTEM_CONFIG
try:
    from SYSTEM_CONFIG import SystemState
except ImportError:
    logger.error("✗ SYSTEM_CONFIG.py not found. Please run 'make init' first.")
    sys.exit(1)


class TaskOrchestrator:
    """Orchestrator for managing and executing tasks in the automation system."""
    
    def __init__(self):
        """Initialize the task orchestrator with system state."""
        try:
            self.system_state = SystemState()
            logger.info(f"✓ TaskOrchestrator initialized | {self.system_state.get_status()}")
        except Exception as e:
            logger.error(f"✗ Failed to initialize TaskOrchestrator: {e}")
            raise
    
    def execute_task(self, task_name):
        """
        Execute a task if the system is in ACTIVE state.
        
        Args:
            task_name (str): Name of the task to execute
            
        Returns:
            bool: True if task executed successfully, False otherwise
        """
        try:
            # Verify system state
            if self.system_state.state != "ACTIVE":
                logger.warning(
                    f"✗ Cannot execute task '{task_name}': "
                    f"System state is {self.system_state.state}, expected ACTIVE"
                )
                return False
            
            # Log task execution
            timestamp = datetime.now().isoformat()
            logger.info(
                f"✓ Executing task: '{task_name}' | "
                f"Mode: {self.system_state.operational_mode} | "
                f"Registry: {self.system_state.registry} | "
                f"Timestamp: {timestamp}"
            )
            
            # Task execution successful
            return True
            
        except Exception as e:
            logger.error(f"✗ Error executing task '{task_name}': {e}")
            return False
    
    def get_system_info(self):
        """Get detailed system information."""
        info = {
            "status": self.system_state.state,
            "registry": self.system_state.registry,
            "operational_mode": self.system_state.operational_mode,
            "full_status": self.system_state.get_status()
        }
        return info


def main():
    """Main entry point for testing the orchestrator."""
    try:
        # Initialize orchestrator
        orchestrator = TaskOrchestrator()
        
        # Display system information
        sys_info = orchestrator.get_system_info()
        logger.info(f"System Information: {sys_info}")
        
        # Test task execution
        test_tasks = [
            "data_validation",
            "process_configuration",
            "deploy_infrastructure"
        ]
        
        logger.info("=" * 60)
        logger.info("Starting Task Execution Pipeline")
        logger.info("=" * 60)
        
        for task in test_tasks:
            success = orchestrator.execute_task(task)
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"Task '{task}': {status}")
        
        logger.info("=" * 60)
        logger.info("Task Execution Pipeline Completed")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"✗ Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
