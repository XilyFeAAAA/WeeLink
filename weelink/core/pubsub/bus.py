# standard library
import heapq
import asyncio
from collections import defaultdict

# local library
from .enum import EventType
from .model import Subscriber
from .dispatcher import Dispatcher
from weelink.core.utils import logger
from weelink.core.message import MessageEvent

# TODO DISPATCHER
class PubSubBroker:

    def __init__(self) -> None:
        self.queue = asyncio.Queue()
        self.event = asyncio.Event()
        self.sub_lock = asyncio.Lock()
        self.dispatcher = Dispatcher()
        self.subscribers: dict[EventType, list[Subscriber]] = defaultdict(list)


    async def subscribe(self, event_type: EventType, priority: int, callback: callable) -> Subscriber:
        """subscribe event"""
        sub = Subscriber(priority, callback, "TODO", event_type)
        async with self.sub_lock:
            heapq.heappush(self.subscribers[event_type], sub)
        return sub


    def unsubscribe(self, event_type: EventType, sub_id: str) -> None:
        """unsubscribe event"""
        subs = self.subscribers.get(event_type, [])
        self.subscribers[event_type] = [sub for sub in subs if sub.id != sub_id]
        heapq.heapify(self.subscribers[event_type])
        
        
    async def publish(self, event: MessageEvent):
        """publish event"""
        await self.queue.put(event)
        self.event.set()
    
    
    async def run(self):
        """轮询队列"""
        while True:
            await self.event.wait()
            
            while not self.queue.empty():
                event = await self.queue.get()
                logger.debug(str(event))
                async with self.sub_lock:
                    subs = list(self.subscribers[event.event_type])
                
                for sub in subs:
                    asyncio.create_task(
                        self.dispatcher.dispatch(sub, event)
                    )
                
            # reset event and wait for notification 
            self.event.clear()
    
    
    async def get_subscribers(self, event_type: EventType) -> list[Subscriber]:
        """获取某个事件的全部订阅者"""
        return self.subscribers.get(event_type, [])

broker = PubSubBroker()