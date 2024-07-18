from typing import Callable
from .enums import Event

class EventManager:
    """
    A class that manages events and their associated functions.

    Attributes:
        events (dict): A dictionary that stores the events and their associated functions.
            The keys are event names, and the values are lists of functions.
    """

    def __init__(self):
        self.events = {
            'CommandNotFound': [],
            'ExceptionDuringCommand': [],
            'ArgumentCastingError': [],
            'CommandReceived': [],
            'InvalidPermissions': []
        } 

    async def add_event(self, event_name: str, function: Callable):
        """
        Add an event to the bot.

        Args:
            event_name (str): The name of the event.
            function (Callable): The function to be executed when the event is triggered.
        """
        new_event_name = event_name.value if isinstance(event_name, Event) else event_name
        if new_event_name in self.events:
            self.events[new_event_name].append(function)
        else:
            raise ValueError(f"Unknown event name '{new_event_name}'")
    
    async def trigger_event(self, event_name: str, *args, **kwargs):
        """
        Trigger an event.

        Args:
            event_name (str): The name of the event.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        new_event_name = event_name.value if isinstance(event_name, Event) else event_name
        if new_event_name in self.events:
            for function in self.events[new_event_name]:
                await function(*args, **kwargs)
        else:
            raise ValueError(f"Unknown event name '{new_event_name}'")
    
    async def remove_event(self, event_name: str, function: Callable):
        """
        Remove an event from the bot.

        Args:
            event_name (str): The name of the event.
            function (Callable): The function to be removed.
        """
        new_event_name = event_name.value if isinstance(event_name, Event) else event_name
        if new_event_name in self.events:
            self.events[new_event_name].remove(function)
        else:
            raise ValueError(f"Unknown event name '{new_event_name}'")