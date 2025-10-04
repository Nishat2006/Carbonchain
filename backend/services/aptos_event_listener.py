"""
Aptos Event Listener Service
Listens for contract events and processes them
"""
import asyncio
import os
from typing import Dict, Any, List, Callable
from datetime import datetime

try:
    from aptos_sdk.client import RestClient
    from aptos_sdk.async_client import RestClient as AsyncRestClient
    APTOS_AVAILABLE = True
except ImportError:
    APTOS_AVAILABLE = False
    print("⚠️  Aptos SDK not installed. Event listener disabled.")
    print("   Install with: pip install aptos-sdk")


class AptosEventListener:
    """Listen for and process Aptos contract events"""
    
    def __init__(self):
        if not APTOS_AVAILABLE:
            return
            
        self.node_url = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
        self.module_address = os.getenv("APTOS_MODULE_ADDRESS", "0x1")
        self.client = RestClient(self.node_url)
        self.async_client = AsyncRestClient(self.node_url)
        
        # Event handlers
        self.handlers = {
            'project_created': [],
            'project_updated': [],
            'project_deleted': [],
            'credits_transferred': [],
        }
        
        # Track last processed sequence numbers
        self.last_sequence = {
            'project_created': 0,
            'project_updated': 0,
            'project_deleted': 0,
            'credits_transferred': 0,
        }
        
        self.running = False
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a handler function for an event type"""
        if event_type in self.handlers:
            self.handlers[event_type].append(handler)
            print(f"✅ Registered handler for {event_type}")
        else:
            print(f"⚠️  Unknown event type: {event_type}")
    
    async def get_events(self, event_type: str, start: int = 0, limit: int = 25) -> List[Dict]:
        """Fetch events from the contract"""
        try:
            event_handle = f"{self.module_address}::registry::EventHandles"
            field_name = f"{event_type}_events"
            
            events = await self.async_client.get_events_by_event_handle(
                self.module_address,
                event_handle,
                field_name,
                start,
                limit
            )
            
            return events
        except Exception as e:
            print(f"❌ Failed to fetch {event_type} events: {e}")
            return []
    
    async def process_event(self, event_type: str, event: Dict):
        """Process a single event"""
        try:
            # Extract event data
            event_data = {
                'type': event_type,
                'data': event.get('data', {}),
                'version': event.get('version'),
                'sequence_number': event.get('sequence_number'),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            print(f"📨 Processing {event_type} event #{event_data['sequence_number']}")
            
            # Call all registered handlers
            for handler in self.handlers.get(event_type, []):
                try:
                    await handler(event_data)
                except Exception as e:
                    print(f"❌ Handler error: {e}")
            
            # Update last processed sequence
            self.last_sequence[event_type] = event_data['sequence_number']
            
        except Exception as e:
            print(f"❌ Failed to process event: {e}")
    
    async def poll_events(self, event_type: str, interval: int = 5):
        """Poll for new events of a specific type"""
        while self.running:
            try:
                # Fetch events starting from last processed
                start = self.last_sequence[event_type] + 1
                events = await self.get_events(event_type, start=start, limit=25)
                
                # Process new events
                for event in events:
                    await self.process_event(event_type, event)
                
                # Wait before next poll
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"❌ Polling error for {event_type}: {e}")
                await asyncio.sleep(interval)
    
    async def start(self, poll_interval: int = 5):
        """Start listening for all events"""
        if not APTOS_AVAILABLE:
            print("⚠️  Aptos SDK not available. Event listener not started.")
            return
        
        print("🎧 Starting Aptos event listener...")
        print(f"   Node: {self.node_url}")
        print(f"   Module: {self.module_address}")
        print(f"   Poll interval: {poll_interval}s")
        
        self.running = True
        
        # Start polling tasks for each event type
        tasks = [
            self.poll_events('project_created', poll_interval),
            self.poll_events('project_updated', poll_interval),
            self.poll_events('project_deleted', poll_interval),
            self.poll_events('credits_transferred', poll_interval),
        ]
        
        await asyncio.gather(*tasks)
    
    def stop(self):
        """Stop listening for events"""
        print("🛑 Stopping event listener...")
        self.running = False


# Example event handlers
async def handle_project_created(event_data: Dict):
    """Handle project created event"""
    data = event_data['data']
    print(f"✅ New project created:")
    print(f"   ID: {data.get('project_id')}")
    print(f"   Owner: {data.get('owner')}")
    print(f"   Name: {data.get('name')}")
    print(f"   Credits: {data.get('carbon_credits', 0) / 100} tons")
    
    # Here you can:
    # - Save to database
    # - Send notifications
    # - Update analytics
    # - Trigger other actions


async def handle_project_updated(event_data: Dict):
    """Handle project updated event"""
    data = event_data['data']
    print(f"📝 Project updated:")
    print(f"   ID: {data.get('project_id')}")
    print(f"   Field: {data.get('field_updated')}")
    
    # Update database, cache, etc.


async def handle_project_deleted(event_data: Dict):
    """Handle project deleted event"""
    data = event_data['data']
    print(f"🗑️  Project deleted:")
    print(f"   ID: {data.get('project_id')}")
    
    # Mark as deleted in database


async def handle_credits_transferred(event_data: Dict):
    """Handle credits transferred event"""
    data = event_data['data']
    print(f"💸 Credits transferred:")
    print(f"   From: {data.get('from')}")
    print(f"   To: {data.get('to')}")
    print(f"   Amount: {data.get('amount', 0) / 100} tons")
    
    # Update balances, notify users, etc.


# Global listener instance
listener = None

def get_event_listener() -> AptosEventListener:
    """Get or create event listener instance"""
    global listener
    if listener is None:
        listener = AptosEventListener()
        
        # Register default handlers
        listener.register_handler('project_created', handle_project_created)
        listener.register_handler('project_updated', handle_project_updated)
        listener.register_handler('project_deleted', handle_project_deleted)
        listener.register_handler('credits_transferred', handle_credits_transferred)
    
    return listener


# Standalone script to run listener
if __name__ == "__main__":
    print("🎧 Aptos Event Listener")
    print("=" * 50)
    
    listener = get_event_listener()
    
    try:
        asyncio.run(listener.start(poll_interval=5))
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        listener.stop()
