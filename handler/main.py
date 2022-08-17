""" Hi """

import re
import asyncio
import inspect
from handler import exceptions
from acord import Message

class App(object):
    def __init__(self, client, prefix: str, case_sensitive: bool) -> None:
        self.bot_instance = client
        self.prefix = prefix
        self.commands = {}
        self.case_sensitive = case_sensitive
        client.on("message_create")(self.on_message_create)

    def command(self, command_name=None):
        def inner(func):
            
            return func
        return inner
    
    async def getArguments(self, func) -> dict:
        """ Gets the arguments from a live function and returns if they are optional or not. """
        arguments = {}
        rawFuncArguments = str(inspect.signature(func)).split()
        for arg in rawFuncArguments:
            arg = arg.replace(",", "").replace(")", "").replace("(", "")
            argName = arg.split("=", 1)[0]
            if len(arg.split("=", 1)) == 2:
                argDefault = arg.split("=", 1)[1]
                arguments[argName] = [False, argDefault]
            else:
                arguments[argName] = [True]
        arguments.pop(list(arguments.keys())[0])
        return arguments

