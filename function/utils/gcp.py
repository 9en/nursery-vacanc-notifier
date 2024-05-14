import json
import os

from google.cloud import secretmanager

from utils.dynaconf import get_config_value
from utils.logger import logger


def gcp_secretmanager() -> dict:
  """秘密情報を取得する

  Returns:
    dict: 秘密情報
  """
  logger.info("Accessing secret")
  client = secretmanager.SecretManagerServiceClient()
  name = f"projects/{os.getenv('GCP_PROJECT_ID')}/secrets/{get_config_value('SECRET_MANAGER_NAME')}/versions/latest"
  response = client.access_secret_version(name=name)
  return json.loads(response.payload.data.decode("UTF-8"))
