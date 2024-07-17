import discord
from handler import Handler, Event

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(
    intents=intents
)

myHandler = Handler(client, "!")

@myHandler.event(Event.CommandNotFound) ## choose from 
async def handle_command_not_found(message: discord.Message):
    await message.channel.send("Command not found.")

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("NzcxMzMxODE3OTYwNjM2NDI2.GOOeF0.q4kV5DNWcCLvaoaWgbNeqASB-2aClMv0_IJWAc")