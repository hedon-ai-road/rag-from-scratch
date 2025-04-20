"""
Service for handling system operations.
"""

import os
import psutil
import platform
from datetime import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SystemService:
    """
    Service for handling system operations and retrieving system information.
    """

    @staticmethod
    async def get_system_info() -> Dict[str, Any]:
        """
        Get system information including CPU, memory, disk, and process details.

        Returns:
            Dict[str, Any]: Dictionary containing system information
        """
        try:
            # Get CPU information
            cpu_count = psutil.cpu_count(logical=True)
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Get memory information
            memory = psutil.virtual_memory()

            # Get disk information
            disk = psutil.disk_usage("/")

            # Get process information
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / (1024 * 1024)  # MB

            # Get system uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            # Get platform information
            system_info = {
                "system": {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "python_version": platform.python_version(),
                    "boot_time": boot_time.isoformat(),
                    "uptime_seconds": uptime.total_seconds(),
                },
                "cpu": {
                    "count": cpu_count,
                    "percent": cpu_percent,
                },
                "memory": {
                    "total": memory.total / (1024 * 1024 * 1024),  # GB
                    "available": memory.available / (1024 * 1024 * 1024),  # GB
                    "percent": memory.percent,
                },
                "disk": {
                    "total": disk.total / (1024 * 1024 * 1024),  # GB
                    "used": disk.used / (1024 * 1024 * 1024),  # GB
                    "free": disk.free / (1024 * 1024 * 1024),  # GB
                    "percent": disk.percent,
                },
                "process": {
                    "memory_mb": process_memory,
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "threads": process.num_threads(),
                    "pid": process.pid,
                },
            }

            return system_info

        except Exception as e:
            logger.error(f"Error getting system information: {e}")
            raise
