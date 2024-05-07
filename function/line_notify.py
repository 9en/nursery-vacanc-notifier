import requests
from loguru import logger

from function.dynaconf import get_config_value
from function.gcp import gcp_secretmanager


SECRET = gcp_secretmanager()


@logger.catch
def line_notify(message: str) -> None:
  logger.info("Sending LINE notification")
  headers = {"Authorization": f"Bearer {SECRET[get_config_value('line_notify_token_id')]}"}
  data = {"message": f"\n{message}"}
  requests.post(get_config_value("line_notify_api"), headers=headers, data=data, timeout=10)
