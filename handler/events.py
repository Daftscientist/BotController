from typing import Callable

from .custom_exceptions import CommandNotFound, ExceptionDuringCommand, ArgumentCastingError, InvalidPermissions
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
        print("hey" + event_name)
        new_event_name = event_name.value if isinstance(event_name, Event) else event_name
        if new_event_name in self.events:
            print("hey")
            print(self.events)
            for function in self.events[new_event_name]:
                await function(*args, **kwargs)
        else:
            print("nahh")
            if event_name == 'CommandNotFound':
                raise CommandNotFound(f"Command not found")
            elif event_name == 'ExceptionDuringCommand':
                raise ExceptionDuringCommand(f"Exception occurred during command execution")
            elif event_name == 'ArgumentCastingError':
                raise ArgumentCastingError(f"Error casting argument")
            elif event_name == 'InvalidPermissions':
                raise InvalidPermissions(f"Invalid permissions")
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