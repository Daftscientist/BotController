# Custom Discord.py Command Handler

This project is a custom command handler for Discord bots, designed as a drop-in replacement for `discord.ext.commands`. It uses a handler class to manage command registration and execution with a focus on simplicity and flexibility.

## Features

- **Command Registration:** Easily register commands using decorators.
- **Prefix Support:** Supports single or multiple command prefixes.
- **Parameter Type Guessing:** Automatically guesses parameter types for commands.
- **Event Handling:** Integrates seamlessly with the Discord.py event system.

## Requirements

- Python 3.7+
- `discord.py` library

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/custom-discord-command-handler.git
    cd custom-discord-command-handler
    ```

2. **Install the required dependencies:**
    ```sh
    pip install discord.py
    ```

## Usage

Here's a quick example to get you started:

1. **Create a new file for your bot (e.g., `bot.py`):**
    ```python
    import discord
    from handler import Handler

    intents = discord.Intents.default()
    intents.message_content = True  # Enable message_content intent

    client = discord.Client(intents=intents)

    myHandler = Handler(client, "!")

    @myHandler.command("hello", "Say hello to the bot")
    async def hello(ctx: discord.Message):
        await ctx.channel.send("Hello!")

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    client.run("YOUR_BOT_TOKEN")
    ```

2. **Run your bot:**
    ```sh
    python bot.py
    ```

## Handler Class

The `Handler` class is the core of this command handling system. It registers commands and handles message events to execute commands based on the prefix and message content.

### Initialization

```python
myHandler = Handler(client, "!")
```

- `client`: An instance of `discord.Client`.
- `prefix`: A string or list of strings representing the command prefix(es).

### Command Registration

Commands are registered using the `@myHandler.command` decorator:

```python
@myHandler.command("command_name", "Description of the command")
async def command_function(ctx: discord.Message, *args):
    # Command logic here
```

### Command Execution

When a message starting with the specified prefix is detected, the handler will parse the message and execute the corresponding command function.

## Example

Here is a more detailed example:

```python
import discord
from handler import Handler

intents = discord.Intents.default()
intents.message_content = True  # Enable message_content intent

client = discord.Client(intents=intents)

myHandler = Handler(client, ["!", "?"])

@myHandler.command("hello", "Say hello to the bot")
async def hello(ctx: discord.Message):
    await ctx.channel.send("Hello!")

@myHandler.command("echo", "Echoes the input back to the user")
async def echo(ctx: discord.Message, *args):
    await ctx.channel.send(" ".join(args))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run("YOUR_BOT_TOKEN")
```

In this example, the bot responds to the `!hello` and `?hello` commands with "Hello!" and echoes the input back to the user with the `!echo` and `?echo` commands.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.