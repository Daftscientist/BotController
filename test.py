import handler
from acord import Client, Intents, Embed

client = Client(intents=Intents.ALL)
commands = handler.App(
    client=client,
    prefix="!", 
    case_sensitive=True
)

@commands.command(command_name="dm")
async def dm_command(message, user, msgToDmTheUser):
    return await message.channel.send(content=f"user: {user}\n the message to dm: {msgToDmTheUser}")

@commands.command("help")
async def help(message):
    embed = Embed(description="Sent using Daftscientist's command handler for acord.")
    await message.channel.send(embed=embed)

client.run("OTE4NTg4NzE1Mjg1MjMzNjg0.YbJcaA.pwc4un4eQ24uLlfgQOPSyBcxOSo")