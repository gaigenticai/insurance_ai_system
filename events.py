"""
Event broker module for the Insurance AI System.
Implements Redis Streams for inter-agent communication.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional

import redis

# Configure logging
logger = logging.getLogger(__name__)

# Get Redis configuration from environment variables
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
REDIS_DB = os.environ.get('REDIS_DB', '0')

# Initialize Redis client
try:
    if REDIS_PASSWORD:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            password=REDIS_PASSWORD,
            db=int(REDIS_DB),
            decode_responses=True
        )
    else:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            db=int(REDIS_DB),
            decode_responses=True
        )
    
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None


def publish_event(event_type: str, payload: Dict[str, Any]) -> bool:
    """
    Publish an event to Redis Streams.
    
    Args:
        event_type: Type of event (e.g., 'underwriting.completed')
        payload: Event payload dictionary
        
    Returns:
        True if successful, False otherwise
    """
    if not redis_client:
        logger.error("Redis client not initialized")
        return False
    
    try:
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Add timestamp and event ID to payload
        full_payload = {
            **payload,
            'event_id': event_id,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type
        }
        
        # Convert payload to string
        payload_str = json.dumps(full_payload)
        
        # Publish to Redis Stream
        stream_name = f"insurance_ai:{event_type}"
        redis_client.xadd(stream_name, {'payload': payload_str})
        
        # Also store in events table if DB is available
        try:
            from db_connection import insert_record
            
            event_data = {
                'event_id': event_id,
                'event_type': event_type,
                'payload': full_payload,
                'created_at': datetime.utcnow(),
                'source': full_payload.get('source', 'system'),
                'institution_id': full_payload.get('institution_id', 'unknown')
            }
            
            insert_record('events', event_data)
        except Exception as e:
            logger.warning(f"Failed to store event in database: {e}")
        
        logger.info(f"Published event {event_type} with ID {event_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        return False


def subscribe_to_events(event_types: List[str], callback: Callable[[Dict[str, Any]], None], 
                        consumer_group: str = 'insurance_ai_agents', 
                        consumer_name: Optional[str] = None) -> None:
    """
    Subscribe to events from Redis Streams.
    
    Args:
        event_types: List of event types to subscribe to
        callback: Function to call when an event is received
        consumer_group: Consumer group name
        consumer_name: Consumer name (defaults to a UUID)
    """
    if not redis_client:
        logger.error("Redis client not initialized")
        return
    
    if not consumer_name:
        consumer_name = f"consumer-{uuid.uuid4().hex[:8]}"
    
    # Create streams and consumer groups if they don't exist
    for event_type in event_types:
        stream_name = f"insurance_ai:{event_type}"
        try:
            # Create stream if it doesn't exist
            redis_client.xinfo_stream(stream_name)
        except redis.exceptions.ResponseError:
            # Stream doesn't exist, create it with an empty message
            redis_client.xadd(stream_name, {'init': 'init'})
        
        try:
            # Create consumer group if it doesn't exist
            redis_client.xinfo_groups(stream_name)
        except redis.exceptions.ResponseError:
            # Group doesn't exist, create it
            redis_client.xgroup_create(stream_name, consumer_group, id='0', mkstream=True)
    
    # Subscribe to streams
    streams = {f"insurance_ai:{event_type}": '>' for event_type in event_types}
    
    logger.info(f"Subscribing to events: {event_types}")
    
    while True:
        try:
            # Read new messages
            messages = redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                streams,
                count=10,
                block=1000
            )
            
            # Process messages
            for stream, stream_messages in messages:
                for message_id, message in stream_messages:
                    try:
                        # Parse payload
                        payload = json.loads(message['payload'])
                        
                        # Call callback
                        callback(payload)
                        
                        # Acknowledge message
                        redis_client.xack(stream, consumer_group, message_id)
                    except Exception as e:
                        logger.error(f"Error processing message {message_id}: {e}")
        except Exception as e:
            logger.error(f"Error reading from streams: {e}")
            time.sleep(1)


class EventSubscriber:
    """Class for subscribing to events."""
    
    def __init__(self, event_types: List[str], consumer_group: str = 'insurance_ai_agents',
                 consumer_name: Optional[str] = None):
        """
        Initialize the event subscriber.
        
        Args:
            event_types: List of event types to subscribe to
            consumer_group: Consumer group name
            consumer_name: Consumer name (defaults to a UUID)
        """
        self.event_types = event_types
        self.consumer_group = consumer_group
        self.consumer_name = consumer_name or f"consumer-{uuid.uuid4().hex[:8]}"
        self.handlers = {}
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a handler for an event type.
        
        Args:
            event_type: Event type to handle
            handler: Function to call when the event is received
        """
        if event_type not in self.event_types:
            self.event_types.append(event_type)
        
        self.handlers[event_type] = handler
    
    def start(self) -> None:
        """Start listening for events."""
        def callback(payload: Dict[str, Any]) -> None:
            event_type = payload.get('event_type')
            if event_type in self.handlers:
                self.handlers[event_type](payload)
        
        subscribe_to_events(self.event_types, callback, self.consumer_group, self.consumer_name)
