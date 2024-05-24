import logging
import os

from google.cloud.logging import Client
from google.cloud.logging_v2.handlers import CloudLoggingHandler

from utils.dynaconf import get_config_value


CLOUD_LOGGING_FORMAT = (
  '{"name": "%(name)s", "level": "%(levelname)s", "pathname": "%(pathname)s", '
  '"lineno": %(lineno)d, "time": "%(asctime)s", "msg": "%(message)s"}'
)
LOCAL_LOGGING_FORMAT = "%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s"


def init_logger() -> logging.Logger:
  """ログを初期化して返すシングルトン関数

  Returns:
      logging.Logger: 初期化されたロガー
  """
  logger = logging.getLogger(get_config_value("PROJECT_NAME"))
  if not logger.handlers:  # Avoid adding handlers multiple times in case of reinitialization
    logger.setLevel(logging.DEBUG)

    env_logger = os.getenv("ENV_LOGGER")
    if env_logger == "local":
      handler = logging.StreamHandler()
      handler.setFormatter(logging.Formatter(LOCAL_LOGGING_FORMAT))
    elif env_logger == "gcloud":
      client = Client()
      handler = CloudLoggingHandler(client)
      handler.setFormatter(logging.Formatter(CLOUD_LOGGING_FORMAT))
    else:
      handler = logging.NullHandler()

    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False  # Avoid duplicate logs in the console

  return logger


def log_decorator(func):
  def wrapper(*args, **kwargs):
    logger = init_logger()  # Each time the function is called, the logger is initialized
    return func(logger, *args, **kwargs)

  return wrapper
