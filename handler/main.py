from dataclasses import dataclass, field
import inspect
from discord.client import Client
from discord import Message
from typing import List, Callable, Any

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
                        raise ValueError(f"Could not cast {arg} to {corresponding_type}")

                await cmd.function(message, *args)
                return

    # Decorator func to add commands
    def command(self, name: str, description: str):
        def decorator(func):
            # Ensure the function is async
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Command function must be a coroutine")
            # Check and guess parameter types once at registration
            param_types = self.check_and_guess_param_types(func)
            self.commands.append(Command(name, description, func, param_types))
            return func
        return decorator

    def register_command(self, name: str, description: str, func: Callable):
        ## make sure the function is async
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Command function must be a coroutine")

        param_types = self.check_and_guess_param_types(func)
        self.commands.append(Command(name, description, func, param_types))