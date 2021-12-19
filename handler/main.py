import asyncio
import inspect
from handler import exceptions
from acord import Message


class App(object):
    def __init__(self, acord_bot_instance, prefix: str, case_sensitive: bool) -> None:
        self.bot_instance = acord_bot_instance
        acord_bot_instance.on("message")(self.on_message)
        self.prefix = prefix
        self.commands = {}
        self.case_sensitive = case_sensitive
    
    def command(self, command_name):
        def inner(func):
            if self.case_sensitive:
                if command_name in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {command_name} already exists.")
            else:
                if command_name.lower() in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {command_name} already exists.")
            self.commands[command_name] = {"function": func, "arguments": ()}
            return func
        return inner
    
    async def on_message(self, message: Message) -> None:
        message_content = message.content
        for command in self.commands:
            functionArguments = inspect.getfullargspec(self.commands[command]['function']).args
            if self.case_sensitive:
                if message_content.startswith(self.prefix + command):
                    if (len(functionArguments) -1) >= 0:
                        arguments = message_content.split(self.prefix + command)[1]
                        if len(arguments) >= len(functionArguments):
                            dictionary_of_arguments = {}
                            functionArguments.remove('message')
                            for item in functionArguments:
                                dictionary_of_arguments[item] = arguments.split()[functionArguments.index(item)]
                            return await self.commands[command]['function'](message, **dictionary_of_arguments)
                        else:
                            raise exceptions.RequiredArgument(f"In command {command}, there was missing arguments.")
                else:
                    if message.content.startswith(self.prefix):
                        command = message.content.split()[0].split("!")[1]
                        raise exceptions.CommandNotFound(f"The command {command} can't be found.")
            else:
                if message_content.startswith(self.prefix.lower() + command.lower()):
                    if (len(functionArguments) -1) >= 0:
                        arguments = message_content.split(self.prefix.lower() + command.lower())[1]
                        if len(arguments) >= len(functionArguments):
                            dictionary_of_arguments = {}
                            functionArguments.remove('message')
                            for item in functionArguments:
                                dictionary_of_arguments[item.lower()] = arguments[functionArguments.index(item.lower())]
                            return await self.commands[command]['function'](message, **dictionary_of_arguments)
                        else:
                            raise exceptions.RequiredArgument(f"In command {command}, there was missing arguments.")
                else:
                    if message.content.startswith(self.prefix):
                        command = message.content.split()[0].split("!")[1]
                        raise exceptions.CommandNotFound(f"The command {command} can't be found.")