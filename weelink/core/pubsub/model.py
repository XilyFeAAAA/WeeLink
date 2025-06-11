# standard library
import uuid
from dataclasses import dataclass, field

# local library
from .enum import EventType


@dataclass(order=True)
class Subscriber:
    priority: int
    callback: callable = field(compare=False)
    plugin_name: str = field(compare=False)
    event_type: EventType = field(compare=False)
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    meta: dict[str, any] = field(default_factory=dict, compare=False)


    def __repr__(self):
        return (f"<Subscriber id={self.id} plugin={self.plugin_name} "
                f"event={self.event_type} priority={self.priority}>")



