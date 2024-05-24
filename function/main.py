from datetime import datetime, timedelta
from typing import Any, Dict

import functions_framework
import pandas as pd
import pytz
from scraping import scrape
from utils.dynaconf import get_config_value
from utils.line_notify import line_notify
from utils.logger import log_decorator


def line_city_post(city: str, update_time: str) -> None:
  """Post the information to LINE for a specific city

  Args:
      city (str): City name
      update_time (str): Update time in the format of %Y-%m-%d %H:%M:%S
  """
  date_obj = datetime.strptime(update_time, "%Y-%m-%d %H:%M:%S")
  notify_message = f"🏢{city}🏢({date_obj.strftime('%Y年%m月%d日')}時点)\n"
  notify_message += f"{get_config_value('REQUEST_URL')[city]}"
  line_notify(notify_message)


@log_decorator
def line_post(logger: Any, df: pd.DataFrame, update_time: str) -> None:
  """Post the information to LINE

  Args:
      logger (Any): Logger object
      df (pd.DataFrame): DataFrame containing the information
      update_time (str): Update time in the format of %Y-%m-%d %H:%M:%S
  """
  for city in get_config_value("REQUEST_URL"):
    logger.info(f"Post to LINE for city: {city} information")
    line_city_post(city, update_time)

    for age in get_config_value("TARGET_AGE"):
      for availability in get_config_value("TARGET_AVAILABILITY"):
        logger.info(f"Post to LINE for city: {city} age: {age}, availability: {availability}")
        message_header = f"👶{age}で{availability}空きあり👶\n"
        notify_message = message_header
        df_target = df[(df["空き"] == availability) & (df["年齢"] == age)]

        # 空きがある場合は情報を送信
        for _, row in df_target.iterrows():
          # 次に追加する文字列
          next_part = f"🏡{row['名称']}\n"
          # 現在のメッセージに追加すると100文字を超える場合は、現在のメッセージを送信
          if len(notify_message + next_part) > get_config_value("LINE_NOTIFY_MAX_MESSAGE_LENGTH"):
            line_notify(notify_message)
            notify_message = message_header
          # 文字列を追加
          notify_message += next_part

        # 最後のメッセージが残っていれば送信
        if notify_message:
          line_notify(notify_message)


def is_within_one_hour_jst(datetime_str: str) -> bool:
  """Check if the datetime is within one hour from now in JST

  Args:
      datetime_str (str): Datetime string in the format of %Y-%m-%d %H:%M:%S

  Returns:
      bool: Whether the datetime is within one hour from now in JST
  """
  jst = pytz.timezone("Asia/Tokyo")
  dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
  dt_jst = jst.localize(dt)
  now_jst = datetime.now(jst)
  delta = now_jst - dt_jst
  return abs(delta) <= timedelta(hours=1)


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
    df, update_time = scrape()

    if is_within_one_hour_jst(update_time):
      logger.debug("Post to LINE")
      line_post(df, update_time)
    else:
      logger.info("No update")
    return {"status": "200"}

  except Exception as e:
    logger.exception(e)
    return {"status": "500", "error": str(e)}
