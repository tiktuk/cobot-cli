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
        Validator("default_resource_id", must_exist=False, is_type_of=str),
    ],
)
