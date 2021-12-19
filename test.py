import handler
from acord import Client, Intents

client = Client(intents=Intents.ALL)
commands = handler.App(client, "!", case_sensitive=True)

@commands.command(command_name="help")
def help_command(message):
    print("gae")




help_command("uwu")