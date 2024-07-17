from dataclasses import dataclass, field
import inspect
from discord.client import Client
from discord import Message
from typing import List, Callable, Any, Union
from .custom_exceptions import CommandNotFound, ExceptionDuringCommand, ArgumentCastingError
from .enums import Event

@dataclass
class Command:
    name: str
    description: str
    function: Callable
    param_types: List[Any] = field(default_factory=list)

class Handler:
    def __init__(self, app: Client, prefix: str | list[str]):
        if not isinstance(app, Client):
            raise TypeError("app must be an instance of discord.Client")
        if not isinstance(prefix, (str, list)) or not all(isinstance(i, str) for i in prefix):
            raise TypeError("prefix must be a string or a list of strings")
        
        if isinstance(prefix, str):
            prefix = [prefix]

        self.app = app
        self.prefix = prefix
        self.commands: List[Command] = []

        self.app.event(self.on_message)

        # Custom events
        self.events = {
            'CommandNotFound': [],
            'ExceptionDuringCommand': [],
            'ArgumentCastingError': [],
            'CommandReceived': []
        }

    def check_and_guess_param_types(self, func: Callable) -> List[Any]:
        # Extract the parameters of the function, skipping the first one (context object)
        params = list(inspect.signature(func).parameters.values())[1:]
        
        param_types = []
        for param in params:
            # Check if the parameter has a type hint
            if param.annotation is not inspect.Parameter.empty:
                param_types.append(param.annotation)
            else:
                # If no type hint, guess the type (implement your own guessing logic here)
                # For now, default to str
                param_types.append(str)
        
        return param_types

    async def on_message(self, message: Message):
        # Ensure we are not processing messages from the bot itself
        if message.author == self.app.user:
            return

        # Check if message starts with any prefix
        if not message.content.startswith(tuple(self.prefix)):
            return

        # Remove the first instance of the prefix
        content = message.content
        for prefix in self.prefix:
            if content.startswith(prefix):
                content = content[len(prefix):]
                break
        
        # We are now left with 'command arg1 arg2 arg3 ...'
        # Split it into a list
        command_arg = content.split(" ")

        # Separate command from args
        command = command_arg[0]
        args = command_arg[1:]

        # Check if the command is valid
        for cmd in self.commands:
            if cmd.name == command:
                param_types = cmd.param_types
                
                # If the function specifies no arguments, ignore all passed arguments
                if not param_types:
                    await cmd.function(message)
                    await self.trigger_event('CommandReceived', message, cmd)
                    return

                # Bundle extra arguments into the last specified argument
                if len(args) > len(param_types):
                    # Join extra arguments with spaces and assign to the last expected argument
                    args = args[:len(param_types) - 1] + [" ".join(args[len(param_types) - 1:])]

                # Cast each arg to the correct param type
                for i, arg in enumerate(args):
                    corresponding_type = param_types[i]
                    try:
                        args[i] = corresponding_type(arg)
                    except ValueError:
                        await self.trigger_event('ArgumentCastingError', message, cmd, arg)
                        return

                try:
                    await cmd.function(message, *args)
                    await self.trigger_event('CommandReceived', message, cmd)
                except Exception as e:
                    await self.trigger_event('ExceptionDuringCommand', message, cmd, e)
                return
        
        # If no matching command found, trigger CommandNotFound event
        await self.trigger_event('CommandNotFound', message)

    # Decorator func to add commands
    def command(self, name: str, description: str):
        def decorator(func):
            # Check and guess parameter types once at registration
            param_types = self.check_and_guess_param_types(func)
            self.commands.append(Command(name, description, func, param_types))
            return func
        return decorator

    # Custom event handling methods
    async def trigger_event(self, event_name: str, *args, **kwargs):
        if event_name in self.events:
            if self.events[event_name]:
                for event_handler in self.events[event_name]:
                    await event_handler(*args, **kwargs)
            else:
                if event_name == 'CommandNotFound':
                    raise CommandNotFound(f"Command not found")
                elif event_name == 'ExceptionDuringCommand':
                    raise ExceptionDuringCommand(f"Exception occurred during command execution")
                elif event_name == 'ArgumentCastingError':
                    raise ArgumentCastingError(f"Error casting argument")
                
    def event(self, event_name: Union[str, Event]):
        def decorator(func):
            new_event_name = event_name
            if isinstance(event_name, Event):
                new_event_name = event_name.value
            if new_event_name in self.events:
                self.events[new_event_name].append(func)
            else:
                raise ValueError(f"Unknown event name '{event_name}'")
            return func
        return decorator
