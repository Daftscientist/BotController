class CommandNotFound(Exception):
    """
        Exception raised when a command is not found.

        Attributes:
            message: The message object.
    """
    pass

class ExceptionDuringCommand(Exception):
    """
    Exception raised when an error occurs during command execution.

    Attributes:
        message: The message object.
        command_name: The name of the command.
        error: The error that occurred.
    """
    pass

class ArgumentCastingError(Exception):
    """
    Exception raised when an error occurs during argument casting.

    Attributes:
        message: The message object.
        command: The command object.
        argument: The argument that caused the error
    """
    pass

class InvalidPermissions(Exception):
    """
    Exception raised when a user does not have the required permissions to execute a command.

    Attributes:
        message: The message object.
        permission_type: The type of permission (USER, CHANNEL, PERMISSION, or SERVER).
        id: The ID of the user, channel
    """
    pass
