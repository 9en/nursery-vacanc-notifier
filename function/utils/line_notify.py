import requests
from utils.dynaconf import get_config_value
from utils.gcp import gcp_secretmanager
from utils.logger import init_logger


logger = init_logger()


def line_notify(message: str) -> None:
  secret = gcp_secretmanager()
  logger.info("Sending LINE notification")
  headers = {"Authorization": f"Bearer {secret[get_config_value('LINE_NOTIFY_TOKEN_ID')]}"}
  data = {"message": f"\n{message}"}
  requests.post(get_config_value("LINE_NOTIFY_API"), headers=headers, data=data, timeout=10)
