from datetime import datetime
from typing import Any

import pandas as pd
from utils.dynaconf import get_config_value
from utils.line_notify import line_notify
from utils.logger import log_decorator


def line_city_post(city: str, update_date: str) -> None:
  """Post the information to LINE for a specific city

  Args:
      city (str): City name
      update_date (str): Update time in the format of %Y-%m-%d
  """
  date_obj = datetime.strptime(update_date, "%Y-%m-%d")
  notify_message = f"🏢{city}🏢({date_obj.strftime('%Y年%m月%d日')}時点)\n"
  notify_message += f"{get_config_value('REQUEST_URL')[city]}"
  line_notify(notify_message)


@log_decorator
def line_post(logger: Any, df: pd.DataFrame, update_date: str) -> None:
  """Post the information to LINE

  Args:
      logger (Any): Logger object
      df (pd.DataFrame): DataFrame containing the information
      update_date (str): Update time in the format of %Y-%m-%d
  """
  # 定員情報を追加
  df["capacity"] = df["capacity"].astype("str")
  df["nursery_name"] = df["nursery_name"] + "(定員:" + df["capacity"] + ")"

  # 都市ごとに情報を送信
  for city in get_config_value("REQUEST_URL"):
    logger.info(f"Post to LINE for city: {city} information")
    line_city_post(city, update_date)

    # 年齢、空き状況ごとに情報を送信
    for age in get_config_value("TARGET_AGE"):

      # 空き状況ごとに情報を送信
      for availability in get_config_value("TARGET_AVAILABILITY"):
        logger.info(f"Post to LINE for city: {city} age: {age}, availability: {availability}")
        message_header = f"👶{age}で{availability}空きあり👶\n"
        notify_message = message_header
        df_target = df[(df["vacancy"] == availability) & (df["age"] == age)]

        # 空きがある場合は情報を送信
        for _, row in df_target.iterrows():
          next_part = f"🏡{row['nursery_name']}\n"
          # 現在のメッセージに追加すると100文字を超える場合は、現在のメッセージを送信
          if len(notify_message + next_part) > get_config_value("LINE_NOTIFY_MAX_MESSAGE_LENGTH"):
            line_notify(notify_message)
            notify_message = message_header
          notify_message += next_part

        # 最後のメッセージが残っていれば送信
        if notify_message:
          line_notify(notify_message)
