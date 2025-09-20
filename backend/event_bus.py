import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)

class EventPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Event:
    """Event data structure for the event bus"""
    event_type: str
    data: Dict[str, Any]
    source: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "correlation_id": self.correlation_id
        }

class EventBus:
    """Event-driven communication system for agent clusters"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.metrics = {
            "events_published": 0,
            "events_processed": 0,
            "failed_events": 0
        }
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to event type: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe a handler from an event type"""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                logger.info(f"Handler unsubscribed from event type: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event type: {event_type}")
    
    async def publish(self, event: Event) -> bool:
        """Publish an event to all subscribers"""
        try:
            self.metrics["events_published"] += 1
            
            # Store in history
            self._add_to_history(event)
            
            # Get handlers for this event type
            handlers = self.handlers.get(event.event_type, [])
            
            if not handlers:
                logger.warning(f"No handlers found for event type: {event.event_type}")
                return True
            
            # Execute handlers based on priority
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        # Run sync handler in thread pool
                        tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, event))
                except Exception as e:
                    logger.error(f"Error preparing handler for event {event.event_id}: {str(e)}")
                    self.metrics["failed_events"] += 1
            
            # Execute all handlers concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Check for exceptions
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Handler {i} failed for event {event.event_id}: {str(result)}")
                        self.metrics["failed_events"] += 1
                    else:
                        self.metrics["events_processed"] += 1
            
            logger.info(f"Event published successfully: {event.event_type} ({event.event_id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_id}: {str(e)}")
            self.metrics["failed_events"] += 1
            return False
    
    async def emit(self, event_type: str, data: Dict[str, Any], source: str, 
                   priority: EventPriority = EventPriority.NORMAL, 
                   correlation_id: Optional[str] = None) -> bool:
        """Convenience method to create and publish an event"""
        event = Event(
            event_type=event_type,
            data=data,
            source=source,
            priority=priority,
            correlation_id=correlation_id
        )
        return await self.publish(event)
    
    def _add_to_history(self, event: Event):
        """Add event to history with size management"""
        self.event_history.append(event)
        
        # Maintain max history size
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
    
    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 50) -> List[Event]:
        """Get recent events, optionally filtered by type"""
        events = self.event_history[-limit:]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return {
            **self.metrics,
            "active_handlers": sum(len(handlers) for handlers in self.handlers.values()),
            "event_types": list(self.handlers.keys()),
            "history_size": len(self.event_history)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive event bus status"""
        return {
            "status": "active",
            "metrics": self.get_metrics(),
            "recent_events": [event.to_dict() for event in self.get_recent_events(limit=10)]
        }

# Global event bus instance
event_bus = EventBus()

# Event type constants
class EventTypes:
    # Intelligence Engine Events
    TRENDS_DISCOVERED = "trends_discovered"
    STRATEGY_READY = "strategy_ready"
    PERFORMANCE_ANALYSIS_READY = "performance_analysis_ready"
    COMPLIANCE_CHECK_COMPLETE = "compliance_check_complete"
    
    # Creation Engine Events
    CONTENT_CREATED = "content_created"
    CONTENT_BATCH_READY = "content_batch_ready"
    VOICE_CLONE_READY = "voice_clone_ready"
    ASSET_GENERATED = "asset_generated"
    
    # Distribution Engine Events
    CONTENT_PUBLISHED = "content_published"
    ENGAGEMENT_UPDATE = "engagement_update"
    MONETIZATION_UPDATE = "monetization_update"
    PUBLISHING_SCHEDULED = "publishing_scheduled"
    
    # System Events
    CLUSTER_STATUS_CHANGE = "cluster_status_change"
    ERROR_OCCURRED = "error_occurred"
    WORKFLOW_COMPLETE = "workflow_complete"
    AUTOMATION_TRIGGER = "automation_trigger"

# Decorator for event handlers
def event_handler(event_type: str, priority: EventPriority = EventPriority.NORMAL):
    """Decorator to register event handlers"""
    def decorator(func):
        # Store handler info for later registration
        if not hasattr(func, '_event_handlers'):
            func._event_handlers = []
        func._event_handlers.append((event_type, priority))
        return func
    return decorator

def register_handlers(instance):
    """Register all event handlers for an instance"""
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if hasattr(attr, '_event_handlers'):
            for event_type, priority in attr._event_handlers:
                event_bus.subscribe(event_type, attr)
                logger.info(f"Registered handler {attr_name} for event {event_type}")