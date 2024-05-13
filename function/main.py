import functions_framework
import pandas as pd
from loguru import logger
from utils.date import get_current_date_in_jst
from utils.dynaconf import get_config_value
from utils.line_notify import line_notify
from utils.scraping import scrape


def line_city_post(city: str) -> None:
  """Post the information to LINE for a specific city

  Args:
    city (str): City name
  """
  notify_message = f"🏢{city}🏢({get_current_date_in_jst().strftime('%Y年%m月%d日')}時点)\n"
  notify_message += f"{get_config_value('REQUEST_URL')[city]}"
  line_notify(notify_message)


def line_post(df: pd.DataFrame) -> None:
  """Post the information to LINE

  Args:
    df (pd.DataFrame): DataFrame
  """
  for city in get_config_value("REQUEST_URL"):
    logger.info(f"Post to LINE for city: {city} information")
    line_city_post(city)

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
            # print(notify_message)
            notify_message = message_header
          # 文字列を追加
          notify_message += next_part

        # 最後のメッセージが残っていれば送信
        if notify_message:
          line_notify(notify_message)
          # print(notify_message


@functions_framework.http
def main(request) -> dict:
  """Cloud Functionのエントリーポイント

  Args:
    request (flask.Request): HTTPリクエストオブジェクト

  Returns:
    str: HTTPレスポンス
  """
  try:
    df, update_time = scrape()
    if update_time == get_current_date_in_jst().strftime("%Y-%m-%d"):
      line_post(df)
    else:
      logger.info("No update")
    return {"status": "200"}  # noqa: TRY300

  except Exception as e:
    logger.exception(e)
    return {"status": "500", "error": str(e)}

