from dataclasses import dataclass, field
import inspect
import re
from typing import List, Callable, Any, Union

from discord import Client, Message, Permissions, Role as discord_Role, User as discord_User, Guild

from .custom_exceptions import CommandNotFound, ExceptionDuringCommand, ArgumentCastingError, InvalidPermissions
from .enums import Event, DiscordPermissions

# Regular expressions to match pings
PING_PATTERN_USER = re.compile(r"<@!?(\d+)>")   # Matches both <@123456789> and <@!123456789>
PING_PATTERN_ROLE = re.compile(r"<@&(\d+)>")    # Matches <@&798135021785448478>

@dataclass
class Command:
    """
    Represents a command that can be executed by the user.

    Attributes:
        name: The name of the command.
        description: A brief description of the command.
        function: The function to be executed when the command is called.
        aliases: A list of aliases for the command.
        param_types: A list of parameter types for the command function.
    """
    name: str
    description: str
    function: Callable
    aliases: List[str] = field(default_factory=list)
    param_types: List[Any] = field(default_factory=list)

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

        self.events = {
            'CommandNotFound': [],
            'ExceptionDuringCommand': [],
            'ArgumentCastingError': [],
            'CommandReceived': [],
            'InvalidPermissions': []
        }

    async def resolve_ping_to_role(self, guild: Guild, role_id_or_ping: Union[int, str]) -> int:
        """
        Resolve a role mention or ID to a role ID.

        Args:
            guild: The guild in which the role exists.
            role_id_or_ping: The role ID or mention.

        Returns:
            The resolved role ID.
        """
        if isinstance(role_id_or_ping, str) and PING_PATTERN_ROLE.match(role_id_or_ping):
            role_id = int(PING_PATTERN_ROLE.match(role_id_or_ping).group(1))
        else:
            role_id = role_id_or_ping

        return role_id

    async def resolve_ping_to_user(self, guild: Guild, user_id_or_ping: Union[int, str]) -> int:
        """
        Resolve a user mention or ID to a user ID.

        Args:
            guild: The guild in which the user exists.
            user_id_or_ping: The user ID or mention.

        Returns:
            The resolved user ID.
        """
        if isinstance(user_id_or_ping, str) and PING_PATTERN_USER.match(user_id_or_ping):
            user_id = int(PING_PATTERN_USER.match(user_id_or_ping).group(1))
        else:
            user_id = user_id_or_ping

        return user_id

    def check_and_guess_param_types(self, func: Callable) -> List[Any]:
        """
        Check and guess the parameter types for a command function.

        Args:
            func: The command function.

        Returns:
            A list of parameter types.
        """
        params = list(inspect.signature(func).parameters.values())[1:]
        
        param_types = []
        for param in params:
            if param.annotation is not inspect.Parameter.empty:
                param_types.append(param.annotation)
            else:
                param_types.append(str)
        
        return param_types

    async def on_message(self, message: Message):
        """
        Handle incoming messages and execute commands if they match.

        Args:
            message: The incoming message.
        """
        if message.author == self.app.user:
            return

        if not any(message.content.startswith(prefix) for prefix in self.prefix):
            return

        content = message.content
        for prefix in self.prefix:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
                break

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

        args = content.split(" ") if content else []

        for cmd in self.commands:
            if cmd.name == command_name or command_name in cmd.aliases:
                param_types = cmd.param_types
                
                if not param_types:
                    await cmd.function(message)
                    await self.trigger_event('CommandReceived', message, cmd)
                    return

                if len(args) > len(param_types):
                    args = args[:len(param_types) - 1] + [" ".join(args[len(param_types) - 1:])]

                for i, arg in enumerate(args):
                    corresponding_type = param_types[i]
                    if corresponding_type == discord_Role:
                        try:
                            args[i] = await self.resolve_ping_to_role(message.guild, arg)
                        except ValueError:
                            await self.trigger_event('ArgumentCastingError', message, cmd, arg)
                            return
                    elif corresponding_type == discord_User:
                        try:
                            args[i] = await self.resolve_ping_to_user(message.guild, arg)
                        except ValueError:
                            await self.trigger_event('ArgumentCastingError', message, cmd, arg)
                            return
                    else:
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
        
        await self.trigger_event('CommandNotFound', message)

    def role_restricted(self, role: discord_Role):
        """
        Decorator to restrict a command to users with a specific role.

        Args:
            role: The required role.

        Returns:
            The decorator function.
        """
        def decorator(func):
            async def wrapper(message: Message, *args):
                if role in message.author.roles:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'ROLE', message, role)
            return wrapper
        return decorator
    
    def user_restricted(self, user_id: list[int]):
        """
        Decorator to restrict a command to specific users.

        Args:
            user_id: The list of allowed user IDs.

        Returns:
            The decorator function.
        """
        if not all(isinstance(i, int) for i in user_id):
            raise TypeError("user_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.author.id in user_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'USER', message, user_id)
            return wrapper
        return decorator

    def channel_restricted(self, channel_id: list[int]):
        """
        Decorator to restrict a command to specific channels.

        Args:
            channel_id: The list of allowed channel IDs.

        Returns:
            The decorator function.
        """
        if not all(isinstance(i, int) for i in channel_id):
            raise TypeError("channel_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.channel.id in channel_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'CHANNEL', message, channel_id)
            return wrapper
        return decorator

    def server_restricted(self, server_id: list[int]):
        """
        Decorator to restrict a command to specific servers.

        Args:
            server_id: The list of allowed server IDs.

        Returns:
            The decorator function.
        """
        if not all(isinstance(i, int) for i in server_id):
            raise TypeError("server_id must be a list of integers")

        def decorator(func):
            async def wrapper(message: Message, *args):
                if message.guild.id in server_id:
                    await func(message, *args)
                else:
                    await self.trigger_event('InvalidPermissions', 'SERVER', message, server_id)
            return wrapper
        return decorator

    def permission_restricted(self, permissions: list[DiscordPermissions]):
        """
        Decorator to restrict a command to users with specific permissions.

        Args:
            permissions: The list of required permissions.

        Returns:
            The decorator function.
        """
        if not all(isinstance(i, DiscordPermissions) for i in permissions):
            raise TypeError("permissions must be a list of DiscordPermissions")

        def decorator(func):
            async def wrapper(message: Message, *args):
                author_permissions = message.author.guild_permissions
                for permission in permissions:
                    if not getattr(author_permissions, permission.value):
                        await self.trigger_event('InvalidPermissions', 'PERMISSION', message, permission)
                        return

                await func(message, *args)

            return wrapper
        return decorator

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
            param_types = self.check_and_guess_param_types(func)
            self.commands.append(Command(name, description, func, aliases, param_types))
            return func
        return decorator

    async def trigger_event(self, event_name: str, *args, **kwargs):
        """
        Trigger a custom event.

        Args:
            event_name: The name of the event.
        """
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
        """
        Decorator to register an event handler.

        Args:
            event_name: The name of the event.

        Returns:
            The decorator function.
        """
        def decorator(func):
            new_event_name = event_name.value if isinstance(event_name, Event) else event_name
            if new_event_name in self.events:
                self.events[new_event_name].append(func)
            else:
                raise ValueError(f"Unknown event name '{new_event_name}'")
            return func
        return decorator
