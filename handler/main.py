from dataclasses import dataclass, field
import inspect
from discord.client import Client
from discord import Message, Permissions, Role as discord_Role
from typing import List, Callable, Any, Union
from .custom_exceptions import CommandNotFound, ExceptionDuringCommand, ArgumentCastingError, InvalidPermissions
from .enums import Event, DiscordPermissions

@dataclass
class Command:
    """
    Represents a command that can be executed by the user.

    Attributes:
        name: The name of the command
        description: A brief description of the command
        aliases: A list of aliases for the command
        function: The function to be executed when the command is called
    """
    name: str
    description: str
    function: Callable
    aliases: List[str] = field(default_factory=list)
    param_types: List[Any] = field(default_factory=list)

class Handler:
    def __init__(self, app: Client, prefix: Union[str, List[str]], case_insensitive: bool = False):
        if not isinstance(app, Client):
            raise TypeError("app must be an instance of discord.Client")
        if not isinstance(prefix, (str, list)) or not all(isinstance(i, str) for i in prefix):
            raise TypeError("prefix must be a string or a list of strings")
        if not isinstance(case_insensitive, bool):
            raise TypeError("case_insensitive must be a boolean")

        if isinstance(prefix, str):
            prefix = [prefix]

        self.app = app
        self.prefix = prefix
        self.case_insensitive = case_insensitive
        self.commands: List[Command] = []

        self.app.event(self.on_message)

        # Custom events
        self.events = {
            'CommandNotFound': [],
            'ExceptionDuringCommand': [],
            'ArgumentCastingError': [],
            'CommandReceived': [],
            'InvalidPermissions': []
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
        if not any(message.content.startswith(prefix) for prefix in self.prefix):
            return

        # Remove the first instance of the prefix
        content = message.content
        for prefix in self.prefix:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
                break

        # Check if content starts with any command name or alias
        command_name = None
        for cmd in self.commands:
            command_start = next((alias for alias in [cmd.name] + cmd.aliases if content.startswith(alias)), None)
            if command_start:
                command_name = command_start
                content = content[len(command_name):].strip()
                break

        if command_name is None:
            await self.trigger_event('CommandNotFound', message)
            return

        # Split content into args
        args = content.split(" ") if content else []

        # Find the corresponding command
        for cmd in self.commands:
            if cmd.name == command_name or command_name in cmd.aliases:
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

    ## decorator func to be placed above the command decorator to check if user has a role
    def role_restricted(self, role: discord_Role):
        def decorator(func):
            async def wrapper(message: Message, *args):
                if role in message.author.roles:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'ROLE', message, role)
                    return
            return wrapper
        return decorator
    
    ## decorator func to be placed above the command decorator to check if users id is in a list
    def user_restricted(self, user_id: list[int]):
        if not all(isinstance(i, int) for i in user_id):
            raise TypeError("user_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.author.id in user_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'USER', message, user_id)
                    return
            return wrapper
        return decorator

    ## channel restricted decorator
    def channel_restricted(self, channel_id: list[int]):
        if not all(isinstance(i, int) for i in channel_id):
            raise TypeError("channel_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.channel.id in channel_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'CHANNEL', message, channel_id)
                    return
            return wrapper
        return decorator

    ## server restricted decorator
    def server_restricted(self, server_id: list[int]):
        if not all(isinstance(i, int) for i in server_id):
            raise TypeError("server_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.guild.id in server_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'SERVER', message, server_id)
                    return
            return wrapper
        return decorator

    def permission_restricted(self, permissions: list[DiscordPermissions]):
        if not all(isinstance(i, DiscordPermissions) for i in permissions):
            raise TypeError("permissions must be a list of DiscordPermissions")

        def decorator(func):
            async def wrapper(message: Message, *args):
                # Check if the author has the specified permissions
                author_permissions = message.author.guild_permissions
                for permission in permissions:
                    if not getattr(author_permissions, permission.value):
                        await self.trigger_event('InvalidPermissions', 'PERMISSION', message, permission)
                        return

                await func(message, *args)

            return wrapper
        return decorator

    # Decorator func to add commands
    def command(self, name: str, description: str, aliases: List[str] = []):
        def decorator(func):
            # Check and guess parameter types once at registration
            param_types = self.check_and_guess_param_types(func)
            self.commands.append(Command(name, description, func, aliases, param_types))
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
                elif event_name == 'InvalidPermissions':
                    raise InvalidPermissions(f"User does not have required permissions")

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
