import asyncio
from handler import exceptions
from acord import Message


class App(object):
    def __init__(self, acord_bot_instance, prefix: str, case_sensitive: bool) -> None:
        self.bot_instance = acord_bot_instance
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
            print(self.commands)
            return func
        return inner
    
    
    async def on_message(self, message: Message) -> None:
        for command in self.commands():
            if self.case_sensitive == True:
                if message.content.startswith() == f"{self.prefix}{command}":
                    return await self.commands[command]['function']()
                else:
                    if message.content.startswith(self.prefix):
                        raise exceptions.CommandNotFound(f"The command {command} can't be found.")
                    else:
                        return None
            else:
                if message.content.lower().startswith() == f"{self.prefix.lower()}{command.lower()}":
                    return await self.commands[command]['function']()
                else:
                    if message.content.startswith(self.prefix):
                        raise exceptions.CommandNotFound(f"The command {command} can't be found.")
                    else:
                        return None
