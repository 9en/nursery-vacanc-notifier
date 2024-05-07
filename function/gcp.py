import json

from google.cloud import secretmanager
from loguru import logger

from function.dynaconf import get_config_value


@logger.catch
def gcp_secretmanager() -> dict:
  """秘密情報を取得する

  Returns:
    dict: 秘密情報
  """
  logger.info("Accessing secret")
  client = secretmanager.SecretManagerServiceClient()
  name = (
    f"projects/{get_config_value('gcp_project_id')}/secrets/{get_config_value('secret_manager_name')}/versions/latest"
  )
  response = client.access_secret_version(name=name)
  return json.loads(response.payload.data.decode("UTF-8"))
