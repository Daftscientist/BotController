class CommandAlreadyExists(Exception):
    pass

class CommandNotFound(Exception):
    pass

class MissingRequiredArgument(Exception):
    pass

class MissingAllArguments(Exception):
    pass

class SpaceInCommandName(Exception):
    pass