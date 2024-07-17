import discord
from handler import Handler

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(intents=intents)

myHandler = Handler(client, "!")

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@myHandler.command("add", "Add two numbers")
async def add(ctx: discord.Message, a: int, b: int):
    await ctx.channel.send(f"{a} + {b} = {a + b}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("NzcxMzMxODE3OTYwNjM2NDI2.GOOeF0.q4kV5DNWcCLvaoaWgbNeqASB-2aClMv0_IJWAc")