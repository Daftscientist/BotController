import enum

import enum
from discord import Permissions

class DiscordPermissions(enum.Enum):
    CREATE_INSTANT_INVITE = 'create_instant_invite'
    KICK_MEMBERS = 'kick_members'
    BAN_MEMBERS = 'ban_members'
    ADMINISTRATOR = 'administrator'
    MANAGE_CHANNELS = 'manage_channels'
    MANAGE_GUILD = 'manage_guild'
    ADD_REACTIONS = 'add_reactions'
    VIEW_AUDIT_LOG = 'view_audit_log'
    PRIORITY_SPEAKER = 'priority_speaker'
    STREAM = 'stream'
    VIEW_CHANNEL = 'view_channel'
    SEND_MESSAGES = 'send_messages'
    SEND_TTS_MESSAGES = 'send_tts_messages'
    MANAGE_MESSAGES = 'manage_messages'
    EMBED_LINKS = 'embed_links'
    ATTACH_FILES = 'attach_files'
    READ_MESSAGE_HISTORY = 'read_message_history'
    MENTION_EVERYONE = 'mention_everyone'
    USE_EXTERNAL_EMOJIS = 'use_external_emojis'
    VIEW_GUILD_INSIGHTS = 'view_guild_insights'
    CONNECT = 'connect'
    SPEAK = 'speak'
    MUTE_MEMBERS = 'mute_members'
    DEAFEN_MEMBERS = 'deafen_members'
    MOVE_MEMBERS = 'move_members'
    USE_VAD = 'use_vad'
    CHANGE_NICKNAME = 'change_nickname'
    MANAGE_NICKNAMES = 'manage_nicknames'
    MANAGE_ROLES = 'manage_roles'
    MANAGE_WEBHOOKS = 'manage_webhooks'
    MANAGE_EMOJIS_AND_STICKERS = 'manage_emojis_and_stickers'
    USE_APPLICATION_COMMANDS = 'use_application_commands'
    REQUEST_TO_SPEAK = 'request_to_speak'
    MANAGE_THREADS = 'manage_threads'
    USE_PUBLIC_THREADS = 'use_public_threads'
    USE_PRIVATE_THREADS = 'use_private_threads'
    USE_EXTERNAL_STICKERS = 'use_external_stickers'
    SEND_MESSAGES_IN_THREADS = 'send_messages_in_threads'
    START_EMBEDDED_ACTIVITIES = 'start_embedded_activities'

class Event(enum.Enum):
    CommandNotFound = "CommandNotFound"
    ArgumentCastingError = "ArgumentCastingError"
    ExceptionDuringCommand = "ExceptionDuringCommand"
    CommandReceived = "CommandReceived"
    InvalidPermissions = "InvalidPermissions"

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