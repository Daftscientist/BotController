from .enums import DiscordPermissions
from .events import EventManager
from discord import Role as discord_Role, Message

class RestrictedManager():
    def __init__(self, event_manager: EventManager):
        self.EventManager = event_manager
    
    def role(self, role: discord_Role):
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
                    await self.EventManager.trigger_event('InvalidPermissions', 'ROLE', message, role)
            return wrapper
        return decorator
    
    def user(self, user_id: list[int]):
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
                    await self.EventManager.trigger_event('InvalidPermissions', 'USER', message, user_id)
            return wrapper
        return decorator

    def channel(self, channel_id: list[int]):
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
                    await self.EventManager.trigger_event('InvalidPermissions', 'CHANNEL', message, channel_id)
            return wrapper
        return decorator

    def server(self, server_id: list[int]):
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
                    await self.EventManager.trigger_event('InvalidPermissions', 'SERVER', message, server_id)
            return wrapper
        return decorator

    def permission(self, permissions: list[DiscordPermissions]):
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
                        await self.EventManager.trigger_event('InvalidPermissions', 'PERMISSION', message, permission)
                        return

                await func(message, *args)

            return wrapper
        return decorator