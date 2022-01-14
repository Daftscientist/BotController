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
        # <!---------------- Events ------------------->
        client.on("message")(self.on_message)
        """
        client.on("connect")(self.on_connect)
        client.on("ready")(self.on_connect)
        client.on("heartbeat")(self.on_heartbeat)
        client.on("resume")(self.on_resume)
        client.on("message_pin")(self.on_message_pin)
        client.on("guild_create")(self.on_guild_create)
        client.on("guild_recv")(self.on_guild_recv)
        client.on("guild_delete")(self.on_guild_delete)
        client.on("guild_outage")(self.on_guild_outage)
        client.on("guild_update")(self.on_guild_update)
        client.on("guild_ban")(self.on_guild_ban)
        client.on("guild_ban_remove")(self.on_guild_ban_remove)
        client.on("emoji_update")(self.on_emoji_update)
        client.on("emojis_update")(self.on_emojis_update)
        client.on("sticker_update")(self.on_sticker_update)
        client.on("stickers_update")(self.on_stickers_update)
        client.on("channel_create")(self.on_channel_create)
        client.on("channel_update")(self.on_channel_update)
        client.on("channel_delete")(self.on_channel_delete)
        client.on("thread_create")(self.on_thread_create)
        client.on("thread_update")(self.on_thread_update)
        client.on("thread_delete")(self.on_thread_delete)
        client.on("thread_sync")(self.on_thread_sync)
        client.on("on_thread_member_update")(self.on_on_thread_member_update)
        client.on("thread_members_update")(self.on_thread_members_update)
        """

    async def CaseSensitive(self, string: str) -> str:
        """ Turns the string lowercase if case sensitive is enabled. """
        if self.case_sensitive:
            return string
        else:
            return string.lower()

    def command(self, command_name=None):
        def inner(func):
            if command_name == None:
                commandName = func.__name__
            else:
                commandName = command_name
            if self.case_sensitive:
                if commandName in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {commandName} already exists.")
            else:
                commandName = commandName.lower()
                if commandName in self.commands:
                    raise exceptions.CommandAlreadyExists(f"The command {commandName} already exists.")
            self.commands[commandName] = func
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

    async def on_message(self, message: Message) -> None:
        """ Checks the message content and if it matches a command, runs the command. """
        # <!---------------- Variables ------------------->
        messageContent = message.content
        prefix = await self.CaseSensitive(self.prefix)
        # <!------------------- General ------------------->
        if messageContent.startswith(prefix):
            commandName = messageContent.replace(prefix, "", 1).split()[0]
            if commandName in self.commands:
                # <!---------------- Variables ------------------->
                functionArgs = await self.getArguments(self.commands[commandName])
                rawVars = messageContent.replace(prefix, "", 1).replace(commandName, "", 1)
                intOfCmdArgs = len(functionArgs) - 1
                messageArguments = rawVars.split(maxsplit=intOfCmdArgs)
                forcedCommandArguments = []
                allCommandArguments = []
                dictOfArgs = {}
                # <!------------------- General ------------------->
                for item in functionArgs:
                    if functionArgs[item][0] == True:
                        forcedCommandArguments.append(item)
                        allCommandArguments.append(item)
                    else:
                        allCommandArguments.append(item)
                if len(forcedCommandArguments) <= len(messageArguments):
                    for index, item in enumerate(functionArgs):
                        try:
                            messageArguments[index]
                            dictOfArgs[item] = messageArguments[index]
                        except IndexError:
                            dictOfArgs[item] = functionArgs[item][1]
                    return await self.commands[commandName](message, **dictOfArgs)
                else:
                    missedVariables = []
                    for loopIndex, item in enumerate(forcedCommandArguments):
                        try:
                            messageArguments[loopIndex]
                        except IndexError:
                            missedVariables.append(item)
                    if len(missedVariables) == 1:
                        raise exceptions.MissingRequiredArgument(f"You are missing the required argument '{message[0]}'.")
                    else:
                        raise exceptions.MissingAllArguments(f"You are missing the following arguments, {str(missedVariables).strip('[]')}.")
            else:
                command = message.content.split()[0].split("!")[1]
                raise exceptions.CommandNotFound(f"The command {command} can't be found.")