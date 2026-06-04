"""
ADB Connector Module
Manages Android Debug Bridge connection and device control
"""

from ppadb.client import Client as AdbClient
from .logger import get_logger

logger = get_logger(__name__)

# Global device instance
_device = None
_client = None

def connect_device(adb_host: str = "127.0.0.1", adb_port: int = 5037, 
                   device_port: int = 5555) -> object:
    """
    Connect to ADB device
    
    Args:
        adb_host: ADB server host (default: localhost)
        adb_port: ADB server port (default: 5037)
        device_port: Device port (default: 5555)
        
    Returns:
        Device object for executing commands
        
    Raises:
        ConnectionError: If connection fails
    """
    global _device, _client
    
    try:
        _client = AdbClient(host=adb_host, port=adb_port)
        _client.remote_connect(adb_host, device_port)
        
        _device = _client.device(f"{adb_host}:{device_port}")
        
        if not _device:
            raise ConnectionError(f"Could not connect to device at {adb_host}:{device_port}")
        
        logger.info(f"✓ ADB connection established: {adb_host}:{device_port}")
        return _device
        
    except Exception as e:
        logger.error(f"✗ ADB connection failed: {e}")
        raise ConnectionError(f"Failed to connect to ADB device: {e}")

def get_device() -> object:
    """
    Get the current device instance
    
    Returns:
        Device object (or None if not connected)
    """
    return _device

def execute_shell_command(command: str) -> str:
    """
    Execute a shell command on the device
    
    Args:
        command: Shell command to execute
        
    Returns:
        Command output
    """
    if _device is None:
        logger.error("Device not connected!")
        raise RuntimeError("Device not connected. Call connect_device() first.")
    
    try:
        output = _device.shell(command)
        logger.debug(f"Executed: {command}")
        return output
    except Exception as e:
        logger.error(f"Shell command failed: {e}")
        raise

def take_screenshot() -> bytes:
    """
    Take a screenshot from the device
    
    Returns:
        Screenshot bytes
    """
    if _device is None:
        raise RuntimeError("Device not connected. Call connect_device() first.")
    
    try:
        return _device.screencap()
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise

def tap_screen(x: int, y: int) -> None:
    """
    Tap the screen at specified coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
    """
    command = f"input tap {x} {y}"
    execute_shell_command(command)

def swipe_screen(x1: int, y1: int, x2: int, y2: int, duration: int = 100) -> None:
    """
    Swipe on the screen
    
    Args:
        x1: Starting X coordinate
        y1: Starting Y coordinate
        x2: Ending X coordinate
        y2: Ending Y coordinate
        duration: Swipe duration in milliseconds
    """
    command = f"input swipe {x1} {y1} {x2} {y2} {duration}"
    execute_shell_command(command)

def restart_app(package_name: str) -> None:
    """
    Force stop and restart an application
    
    Args:
        package_name: Package name of the app (e.g., "com.supercell.clashofclans")
    """
    try:
        logger.info(f"Force stopping {package_name}...")
        execute_shell_command(f"am force-stop {package_name}")
        
        logger.info(f"Starting {package_name}...")
        execute_shell_command(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        
        logger.info(f"✓ App restarted: {package_name}")
    except Exception as e:
        logger.error(f"App restart failed: {e}")
        raise
