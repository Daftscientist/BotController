from dataclasses import dataclass, field
from typing import Any, Callable, List
from .parsing import Parsing

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

    def __post_init__(self):
        self.aliases.append(self.name)
        self.aliases = list(set(self.aliases))
    
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

async def add_command(commands: list, name: str, description: str, function: Callable, aliases: List[str] = None):
    """
    Add a command to the bot.

    Args:
        name: The name of the command.
        description: A brief description of the command.
        function: The function to be executed when the command is called.
        aliases: A list of aliases for the command.
    """

    param_types = Parsing.param_types(function)
    commands.append(Command(name, description, function, aliases, param_types))
