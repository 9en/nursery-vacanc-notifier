from datetime import datetime
from typing import Any, Dict

import functions_framework
import pytz
from bigquery_job import BigQueryJob
from post import line_post
from scraping import scrape
from utils.dynaconf import get_config_value
from utils.logger import log_decorator


def is_same_date(datetime_str: str) -> bool:
  """Check if the datetime is within one hour from now in JST

  Args:
      datetime_str (str): Datetime string in the format of %Y-%m-%d

  Returns:
      bool: Whether the datetime is within one hour from now in JST
  """
  jst = pytz.timezone("Asia/Tokyo")
  dt = datetime.strptime(datetime_str, "%Y-%m-%d")
  dt_jst = jst.localize(dt)
  now_jst = datetime.now(jst)
  return dt_jst.date() == now_jst.date()


@functions_framework.http
@log_decorator
def main(logger: Any, request: Any) -> Dict[str, Any]:
  """Main function

  Args:
      logger (Any): Logger object
      request (Any): HTTPリクエストオブジェクト

  Returns:
      dict: HTTPレスポンス
  """
  try:
    logger.info("Start scraping")
    df, update_date = scrape()

    logger.info("Check BigQuery Table")
    bq = BigQueryJob()
    bq_bytes = bq.run_query("dry_run", update_date)

    if is_same_date(update_date) and bq_bytes == 0:
      logger.info("Load BigQuery Table")
      bq.load(df)

      logger.debug("Post to LINE")
      df = df[df["vacancy"].isin(get_config_value("TARGET_AVAILABILITY"))]
      df = df[df["age"].isin(get_config_value("TARGET_AGE"))]
      line_post(df, update_date)
    else:
      logger.info("No update")

    return {"status": "200"}

  except Exception as e:
    logger.exception(e)
    return {"status": "500", "error": str(e)}
