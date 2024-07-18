import discord
from botcontroller import Handler, Command

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(
    intents=intents
)

myHandler = Handler(client, "!")

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("")