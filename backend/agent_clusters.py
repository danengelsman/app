import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

from event_bus import event_bus, Event, EventTypes, EventPriority, event_handler, register_handlers
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ClusterStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ClusterMetrics:
    """Metrics for cluster performance tracking"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_processing_time: float = 0.0
    last_activity: Optional[datetime] = None
    uptime_start: datetime = None
    
    def __post_init__(self):
        if self.uptime_start is None:
            self.uptime_start = datetime.now(timezone.utc)

class BaseCluster(ABC):
    """Base class for all agent clusters"""
    
    def __init__(self, cluster_name: str, description: str):
        self.cluster_name = cluster_name
        self.description = description
        self.status = ClusterStatus.IDLE
        self.metrics = ClusterMetrics()
        self.llm_chat = LlmChat(api_key=os.environ.get('EMERGENT_LLM_KEY'))
        self.config = {}
        
        # Register event handlers
        register_handlers(self)
        
        logger.info(f"Initialized cluster: {cluster_name}")
    
    async def start(self):
        """Start the cluster"""
        self.status = ClusterStatus.IDLE
        await self._emit_status_change()
        logger.info(f"Started cluster: {self.cluster_name}")
    
    async def stop(self):
        """Stop the cluster"""
        self.status = ClusterStatus.MAINTENANCE
        await self._emit_status_change()
        logger.info(f"Stopped cluster: {self.cluster_name}")
    
    async def _emit_status_change(self):
        """Emit status change event"""
        await event_bus.emit(
            EventTypes.CLUSTER_STATUS_CHANGE,
            {
                "cluster": self.cluster_name,
                "status": self.status.value,
                "metrics": self._get_metrics_dict()
            },
            source=self.cluster_name
        )
    
    def _get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        uptime = (datetime.now(timezone.utc) - self.metrics.uptime_start).total_seconds()
        return {
            "tasks_completed": self.metrics.tasks_completed,
            "tasks_failed": self.metrics.tasks_failed,
            "average_processing_time": self.metrics.average_processing_time,
            "uptime_seconds": uptime,
            "last_activity": self.metrics.last_activity.isoformat() if self.metrics.last_activity else None
        }
    
    async def _update_metrics(self, processing_time: float, success: bool = True):
        """Update cluster metrics"""
        self.metrics.last_activity = datetime.now(timezone.utc)
        
        if success:
            self.metrics.tasks_completed += 1
        else:
            self.metrics.tasks_failed += 1
        
        # Update average processing time
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total_tasks > 1:
            self.metrics.average_processing_time = (
                (self.metrics.average_processing_time * (total_tasks - 1) + processing_time) / total_tasks
            )
        else:
            self.metrics.average_processing_time = processing_time
    
    async def _handle_error(self, error: Exception, context: str):
        """Handle errors with logging and event emission"""
        logger.error(f"Error in {self.cluster_name} - {context}: {str(error)}")
        
        await event_bus.emit(
            EventTypes.ERROR_OCCURRED,
            {
                "cluster": self.cluster_name,
                "error": str(error),
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            source=self.cluster_name,
            priority=EventPriority.HIGH
        )
        
        self.status = ClusterStatus.ERROR
        await self._emit_status_change()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        return {
            "cluster_name": self.cluster_name,
            "description": self.description,
            "status": self.status.value,
            "metrics": self._get_metrics_dict(),
            "config": self.config
        }
    
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - must be implemented by subclasses"""
        pass

# Import os here since it's needed
import os