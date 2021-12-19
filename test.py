import handler
from acord import Client, Intents

client = Client(intents=Intents.ALL)
commands = handler.App(client, "!", case_sensitive=True)

@commands.command(command_name="dm")
async def dm_command(message, user, msgToDmTheUser):
    return await message.channel.send(content=f"user: {user}\n the message to dm: {msgToDmTheUser}")

client.run("OTE4NTg4NzE1Mjg1MjMzNjg0.YbJcaA.N0wp8VZwwXMoEpgOyEmHoxzHjtE")