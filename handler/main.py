from typing import List, Callable, Any, Union
from discord import Client, Message, Guild
from .restricted import RestrictedManager
from .enums import Event
from .command import Command
from .parsing import Parsing
from .events import EventManager
from .utils import is_command_message, extract_command_info, execute_command

class Handler:
    """
    Handler for processing commands and events in a Discord bot.

    Attributes:
        app: The Discord client instance.
        prefix: The prefix(es) for commands.
        case_insensitive: Whether command names are case insensitive.
        commands: A list of registered commands.
        events: A dictionary of custom events and their handlers.
    """

    def __init__(self, app: Client, prefix: Union[str, List[str]], case_insensitive: bool = False):
        if not isinstance(prefix, (str, list)) or not all(isinstance(i, str) for i in prefix):
            raise TypeError("prefix must be a string or a list of strings")

        if isinstance(prefix, str):
            prefix = [prefix]

        self.app = app
        self.prefix = prefix
        self.case_insensitive = case_insensitive
        self.commands: List[Command] = []

        self.EventManager = EventManager()
        self.Restricted = RestrictedManager(self.EventManager)

        self.app.event(self.on_message)

    async def on_message(self, message: Message):
        """
        Event handler for processing messages.

        Args:
            message: The message object
        
        Returns:
            None
        """
        if message.author == self.app.user:
            return

        if not is_command_message(self.prefix, message):
            return

        command_name, args = extract_command_info(self.prefix, self.commands, message)
        if not command_name:
            await self.EventManager.trigger_event('CommandNotFound', message)
            return

        try:
            await execute_command(self.commands, self.EventManager, message, command_name, args)
        except Exception as e:
            await self.EventManager.trigger_event('ExceptionDuringCommand', message, command_name, e)

    def command(self, name: str, description: str, aliases: List[str] = []):
        """
        Decorator to register a command.

        Args:
            name: The name of the command.
            description: A brief description of the command.
            aliases: A list of aliases for the command.

        Returns:
            The decorator function.
        """
        def decorator(func):
            param_types = Parsing.param_types(func)
            self.commands.append(Command(name, description, func, aliases, param_types))
            return func
        return decorator

    def event(self, event_name: Union[str, Event]):
        """
        Decorator to register an event handler.

        Args:
            event_name: The name of the event.

        Returns:
            The decorator function.
        """
        async def decorator(func):
            await self.EventManager.add_event(event_name, func)
            return func
        return decorator
