from dynaconf import Dynaconf, Validator
import os.path

settings = Dynaconf(
    envvar_prefix="COBOT",
    settings_files=[
        "/etc/cobot/settings.toml",  # system wide
        os.path.expanduser("~/.config/cobot/settings.toml"),  # user specific
        "settings.toml",  # local
    ],
    load_dotenv=True,
    validators=[
        Validator("space_id", must_exist=True, is_type_of=str),
        Validator("space_subdomain", must_exist=True, is_type_of=str),
        Validator(
            "api_base", must_exist=True, is_type_of=str, default="https://api.cobot.me"
        ),
        Validator("access_token", must_exist=True, is_type_of=str),
        Validator("default_resource_id", is_type_of=str),
        Validator(
            "data_dir",
            default="~/.local/share/cobot",
            is_type_of=str,
        ),
        Validator(
            "monitor_days_ahead",
            default=30,
            is_type_of=int,
        ),
        Validator(
            "log_file",
            default="logs/cobot.log",
            is_type_of=str,
        ),
        # Telegram configuration
        Validator("telegram_bot_token", is_type_of=str),
        Validator("telegram_chat_id", is_type_of=str),
    ],
)

# Ensure data_dir is expanded and exists
settings.data_dir = os.path.expanduser(str(settings.data_dir))
os.makedirs(settings.data_dir, exist_ok=True)

# Ensure log file path is absolute and its directory exists
settings.log_file = os.path.join(settings.data_dir, str(settings.log_file))
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
