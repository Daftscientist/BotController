import asyncio
import inspect
from handler import exceptions
from acord import Message

class App(object):
    def __init__(self, client, prefix: str, case_sensitive: bool) -> None:
        self.bot_instance = client
        client.on("message")(self.on_message)
        self.prefix = prefix
        self.commands = {}
        self.case_sensitive = case_sensitive

    async def CaseSensitive(self, string: str) -> str:
        """ Turns the string lowercase if case sensitive is enabled. """
        if self.case_sensitive:
            return string
        else:
            return string.lower()

    def command(self, command_name):
        def inner(func):
            if self.case_sensitive:
                if command_name in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {command_name} already exists.")
            else:
                if command_name.lower() in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {command_name} already exists.")
            self.commands[command_name] = func
            return func
        return inner
    
    async def checkIfOptionalArg(self, func, argument):
        """ Checks if a param in a command is optional. """
        for arg in str(inspect.signature(func)).split():
            item = arg.replace(",", "").replace(")", "").replace("(", "")
            newitem = item.split("=")[0]
            if newitem == argument:
                if "=" in item:
                    return True
                else:
                    return False
            else:
                pass

    async def on_message(self, message: Message) -> None:
        """ Checks the message content and if it matches a command, runs the command. """
        message_content = message.content
        for command in self.commands:
            functionArguments = inspect.getfullargspec(self.commands[command]).args
            if message_content.startswith(await self.CaseSensitive(self.prefix) + await self.CaseSensitive(command)):
                if (len(functionArguments) -1) >= 0:
                    arguments = message_content.split(await self.CaseSensitive(self.prefix) + await self.CaseSensitive(command))[1]
                    if len(arguments) >= (len(functionArguments) - 1):
                        dictionary_of_arguments = {}
                        functionArguments.remove('message')
                        nonLastArguments = []
                        for item in functionArguments:
                            if len(functionArguments) == (functionArguments.index(item) + 1):
                                print(f"{item}, was the last argument in the func")
                                for item in nonLastArguments:
                                    print(item)
                            else:
                                nonLastArguments.append(item)
                            dictionary_of_arguments[await self.CaseSensitive(item)] = await self.CaseSensitive(arguments.split()[functionArguments.index(item)])
                        return await self.commands[command](message, **dictionary_of_arguments)
                    else:
                        raise exceptions.RequiredArgument(f"In command {command}, there was missing arguments.")
            else:
                pass
        if message.content.startswith(self.prefix):
            command = message.content.split()[0].split("!")[1]
            raise exceptions.CommandNotFound(f"The command {command} can't be found.")