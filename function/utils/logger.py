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
  """ログを初期化する関数

  Returns:
      logging.Logger: 初期化されたロガー
  """
  logger = logging.getLogger(get_config_value("PROJECT_NAME"))
  logger.setLevel(logging.DEBUG)

  if os.getenv("ENV_LOGGER") == "local":
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOCAL_LOGGING_FORMAT))
  elif os.getenv("ENV_LOGGER") == "gcloud":
    client = Client()
    handler = CloudLoggingHandler(client)
    handler.setFormatter(logging.Formatter(CLOUD_LOGGING_FORMAT))

  if not logger.handlers:  # Avoid adding handlers multiple times in case of reinitialization
    logger.addHandler(handler)

  return logger
