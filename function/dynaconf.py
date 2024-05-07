import sys


sys.path.insert(0, "/usr/local/lib/python3.11/site-packages")

from dynaconf import Dynaconf


settings = Dynaconf(
  environments=True,
  settings_files="/app/function/settings.toml",
)


def get_config_value(key: str) -> str:
  return settings[key]
