from dynaconf import Dynaconf


settings = Dynaconf(environments=True, settings_files="settings.toml")

def get_config_value(key: str) -> str:
  return settings[key]
