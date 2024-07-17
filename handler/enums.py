import enum

class Event(enum.Enum):
    CommandNotFound = "CommandNotFound"
    ArgumentCastingError = "ArgumentCastingError"
    ExceptionDuringCommand = "ExceptionDuringCommand"
    CommandReceived = "CommandReceived"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    @classmethod
    def get_event(cls, value):
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Unknown event name '{value}'")