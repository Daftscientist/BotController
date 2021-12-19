import handler
from acord import Client, Intents

client = Client(intents=Intents.ALL)
commands = handler.App(client, "!", case_sensitive=True)

@commands.command(command_name="help")
def help_command(message):  ## need to make messafe have value
    print("gae")




help_command("uwu")
