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
        for command in self.commands:
            if self.case_sensitive == True:
                if message.content.startswith(f"{self.prefix}{command}"):
                    argsInCommand = len(inspect.getfullargspec(self.commands[command]['function']).args) - 1
                    if argsInCommand >= 0:
                        argsInUsersCommand = message.content.split(f"{self.prefix}{command} ")[1].split()
                        TheMessage = message.content.split(f"{self.prefix}{command} ")[1].split()
                        arguments = argsInCommand
                        if len(TheMessage) >= arguments:
                            allNeededArgs = inspect.getfullargspec(self.commands[command]['function']).args
                            allNeededArgs.remove('message')
                            dictOfArgs = {}
                            for item in allNeededArgs:
                                dictOfArgs[item] = TheMessage[allNeededArgs.index(item)]
                            return await self.commands[command]['function'](message, **dictOfArgs)
                        else:
                            raise exceptions.RequiredArgument(f"In command {command}, there was missing arguments.")
                    else:
                        return await self.commands[command]['function'](message)
                else:
                    if message.content.startswith(self.prefix):
                        yes = message.content.split()[0]
                        yes = yes.split("!")[1]
                        raise exceptions.CommandNotFound(f"The command {yes} can't be found.")
                    else:
                        return None
            else:
                if message.content.lower().startswith(f"{self.prefix.lower()}{command.lower()}"):
                    return await self.commands[command]['function'](message)
                else:
                    if message.content.startswith(self.prefix):
                        yes = message.content.split()[0]
                        yes = yes.split("!")[1]
                        raise exceptions.CommandNotFound(f"The command {command} can't be found.")
                    else:
                        return None

