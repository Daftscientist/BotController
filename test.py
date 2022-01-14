import handler
import acord
from acord import Client, Intents

client = Client(intents=Intents.ALL)
commands = handler.App(
    client=client,
    prefix="!", 
    case_sensitive=True
)

@commands.command()
async def hdgyhbf(ctx, user, message, dm=False):
    await ctx.channel.send(content=f"{user}\n{message}\n{dm}")


client.run("OTE4NTg4NzE1Mjg1MjMzNjg0.YbJcaA.pwc4un4eQ24uLlfgQOPSyBcxOSo")