import discord
from handler import Handler, Event, DiscordPermissions

from discord import Role

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(
    intents=intents
)

myHandler = Handler(client, "!")

@myHandler.event(Event.CommandNotFound) ## choose from 
async def handle_command_not_found(message: discord.Message):
    await message.channel.send("Command not found.")

@myHandler.Restricted.permission([DiscordPermissions.ADMINISTRATOR])
@myHandler.command("hello world", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

## echo command
@myHandler.command("echo", "Echo a message")
async def echo(ctx: discord.Message, message: str):
    await ctx.channel.send(message)

## multi arg cmd
@myHandler.command("add", "Add two numbers")
async def add(ctx: discord.Message, a: int, b: int):
    await ctx.channel.send(f"{a} + {b} = {a + b}")

@myHandler.Restricted.permission([DiscordPermissions.ADMINISTRATOR])
@myHandler.command("role", "Add a role to a user")
async def role(ctx: discord.Message, role_id: discord.Role, user_id: discord.User):
    try:
        guild = ctx.guild
        user = await guild.fetch_member(user_id)
        role = guild.get_role(role_id)

        if user is None:
            await ctx.channel.send(f"User with ID {user_id} not found.")
            return
        
        if role is None:
            await ctx.channel.send(f"Role with ID {role_id} not found.")
            return
        
        await user.add_roles(role)
        await ctx.channel.send(f"Role {role.name} added to user {user.display_name}.")
    
    except discord.Forbidden:
        await ctx.channel.send("I do not have permission to manage roles.")
    
    except discord.HTTPException as e:
        await ctx.channel.send(f"An error occurred: {e}")
    
    except Exception as e:
        await ctx.channel.send(f"Unexpected error: {e}")


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("NzcxMzMxODE3OTYwNjM2NDI2.GOOeF0.q4kV5DNWcCLvaoaWgbNeqASB-2aClMv0_IJWAc")