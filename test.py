import discord
from handler import Handler, Command

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(intents=intents)

myHandler = Handler(client, "!")

@myHandler.event("CommandNotFound")
async def handle_command_not_found(message: discord.Message):
    await message.channel.send("Command not found.")

@myHandler.event("ArgumentCastingError")
async def handle_argument_casting_error(message: discord.Message, command: Command, arg: str):
    await message.channel.send(f"Error casting argument '{arg}' for command '{command.name}'.")

@myHandler.event("ExceptionDuringCommand")
async def handle_exception_during_command(message: discord.Message, command: Command, exception: Exception):
    await message.channel.send(f"Exception occurred during execution of command '{command.name}': {exception}")

@myHandler.event("CommandReceived")
async def handle_command_received(message: discord.Message, command: Command):
    await message.channel.send(f"Command '{command.name}' received.")

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@myHandler.command("add", "Add two numbers")
async def add(ctx: discord.Message, a: int, b: int):
    await ctx.channel.send(f"{a} + {b} = {a + b}")

@myHandler.command("echo", "Echoes the input back to the user")
async def echo(ctx: discord.Message, *args):
    await ctx.channel.send(" ".join(args))

@myHandler.command("repeat", "Repeats the first argument and bundles the rest")
async def repeat(ctx: discord.Message, first_arg: str, rest_args: str):
    await ctx.channel.send(f"First: {first_arg}, Rest: {rest_args}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("NzcxMzMxODE3OTYwNjM2NDI2.GOOeF0.q4kV5DNWcCLvaoaWgbNeqASB-2aClMv0_IJWAc")