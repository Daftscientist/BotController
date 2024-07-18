from discord import Message, Role as discord_Role, User as discord_User

from .events import EventManager
from .parsing import Parsing


def is_command_message(prefix_list, message: Message) -> bool:
    return any(message.content.startswith(prefix) for prefix in prefix_list)

def extract_command_info(prefix_list, commands, message: Message) -> tuple:
    """
    Extract the command name and arguments from a message.

    Args:
        
        message: The message object.
    """
    content = message.content
    for prefix in prefix_list:
        if content.startswith(prefix):
            content = content[len(prefix) :].strip()
            break

    command_name = None
    for cmd in commands:
        command_start = next(
            (alias for alias in [cmd.name] + cmd.aliases if content.startswith(alias)),
            None,
        )
        if command_start:
            command_name = command_start
            content = content[len(command_name) :].strip()
            break

    args = content.split(" ") if content else []
    return command_name, args


async def execute_command(commands, event_manager: EventManager, message: Message, command_name: str, args: list):
    """
    Execute a command based on the message content.

    Args:
        message: The message object.
        command_name: The name of the command.
        args: The arguments for the command.
    """
    for cmd in commands:
        if cmd.name == command_name or command_name in cmd.aliases:
            param_types = cmd.param_types if cmd.param_types else []

            if len(args) > len(param_types):
                args = args[: len(param_types) - 1] + [
                    " ".join(args[len(param_types) - 1 :])
                ]

            parsed_args = []
            for i, arg in enumerate(args):
                corresponding_type = param_types[i] if i < len(param_types) else str
                try:
                    if corresponding_type == discord_Role:
                        parsed_args.append(Parsing.resolve_role(arg))
                    elif corresponding_type == discord_User:
                        parsed_args.append(Parsing.resolve_user(arg))
                    else:
                        parsed_args.append(corresponding_type(arg))
                except ValueError:
                    await event_manager.trigger_event(
                        "ArgumentCastingError", message, cmd, arg
                    )
                    return

            try:
                await cmd.function(message, *parsed_args)
                await event_manager.trigger_event("CommandReceived", message, cmd)
            except Exception as e:
                await event_manager.trigger_event(
                    "ExceptionDuringCommand", message, cmd, e
                )
            return
