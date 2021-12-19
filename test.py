import handler
from acord import Client, Intents

client = Client(intents=Intents.ALL)
commands = handler.App(client, "!", case_sensitive=True)

@commands.command(command_name="help")
async def help_command(message):
    return await message.channel.send(content="pong")

client.run("OTE4NTg4NzE1Mjg1MjMzNjg0.YbJcaA.N0wp8VZwwXMoEpgOyEmHoxzHjtE")