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
    ],
)

# Ensure data_dir is expanded and exists
settings.data_dir = os.path.expanduser(str(settings.data_dir))
os.makedirs(settings.data_dir, exist_ok=True)
