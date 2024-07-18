import discord
from botcontroller import Handler, Event, DiscordPermissions

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(
    intents=intents
)

myHandler = Handler(client, "!")

@myHandler.event(Event.CommandNotFound)
async def handle_command_not_found(message: discord.Message):
    await message.channel.send("Command not found.")

@myHandler.Restricted.permission([DiscordPermissions.CHANGE_NICKNAME])
@myHandler.command("nick", "Change the users nickname")
async def change_nickname(ctx: discord.Message, user: discord.User, nickname: str):
    await ctx.guild.get_member(user.id).edit(nick=nickname)

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("")