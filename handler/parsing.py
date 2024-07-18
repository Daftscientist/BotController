import inspect
from discord import Guild
from typing import Any, Callable, List, Union
import re

PING_PATTERN_USER = re.compile(r"<@!?(\d+)>")   # Matches both <@123456789> and <@!123456789>
PING_PATTERN_ROLE = re.compile(r"<@&(\d+)>")    # Matches <@&798135021785448478>

class Parsing:
    """
    Utility class for parsing and resolving command arguments.
    """
    
    @staticmethod
    def resolve_role(role_id_or_ping: Union[int, str]) -> int:
        """
        Resolve a role mention or ID to a role ID.

        Args:
            role_id_or_ping: The role ID or mention.

        Returns:
            The resolved role ID.
        """
        if isinstance(role_id_or_ping, str) and PING_PATTERN_ROLE.match(role_id_or_ping):
            role_id = int(PING_PATTERN_ROLE.match(role_id_or_ping).group(1))
        else:
            role_id = role_id_or_ping

        return role_id
    
    @staticmethod
    def resolve_user(user_id_or_ping: Union[int, str]) -> int:
        """
        Resolve a user mention or ID to a user ID.

        Args:
            user_id_or_ping: The user ID or mention.

        Returns:
            The resolved user ID.
        """
        if isinstance(user_id_or_ping, str) and PING_PATTERN_USER.match(user_id_or_ping):
            user_id = int(PING_PATTERN_USER.match(user_id_or_ping).group(1))
        else:
            user_id = user_id_or_ping

        return user_id
    
    @staticmethod
    def param_types(func: Callable) -> List[Any]:
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
                ## guess the type
                param_types.append(str)
        
        return param_types