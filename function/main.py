import functions_framework
import pandas as pd
from loguru import logger

from function.date import get_current_date_in_jst
from function.dynaconf import get_config_value
from function.line_notify import line_notify
from function.scraping import scrape


def line_city_post(city: str) -> None:
  """Post the information to LINE for a specific city

  Args:
    city (str): City name
  """
  notify_message = f"🏢{city}🏢({get_current_date_in_jst().strftime('%Y年%m月%d日')}時点)\n"
  notify_message += f"{get_config_value('request_url')[city]}"
  line_notify(notify_message)


def line_post(df: pd.DataFrame) -> None:
  """Post the information to LINE

  Args:
    df (pd.DataFrame): DataFrame
  """
  for city in get_config_value("request_url"):
    logger.info(f"Post to LINE for city: {city} information")
    line_city_post(city)

    for age in get_config_value("target_age"):
      for availability in get_config_value("target_availability"):
        logger.info(f"Post to LINE for city: {city} age: {age}, availability: {availability}")
        message_header = f"👶{age}で{availability}空きあり👶\n"
        notify_message = message_header
        df_target = df[(df["空き"] == availability) & (df["年齢"] == age)]

        # 空きがある場合は情報を送信
        for _, row in df_target.iterrows():
          # 次に追加する文字列
          next_part = f"🏡{row['名称']}\n"
          # 現在のメッセージに追加すると100文字を超える場合は、現在のメッセージを送信
          if len(notify_message + next_part) > get_config_value("line_notify_max_message_length"):
            line_notify(notify_message)
            # print(notify_message)
            notify_message = message_header
          # 文字列を追加
          notify_message += next_part

        # 最後のメッセージが残っていれば送信
        if notify_message:
          line_notify(notify_message)
          # print(notify_message

@functions_framework.http
def main(request) -> None:
  """Cloud Functionのエントリーポイント

  Args:
    request (flask.Request): HTTPリクエストオブジェクト

  Returns:
    str: HTTPレスポンス
  """
  with logger.catch():
    df, update_time = scrape()
    if update_time == get_current_date_in_jst().strftime("%Y-%m-%d"):
      line_post(df)
    else:
      logger.info("No update")
  return {"status": "200"}

