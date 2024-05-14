from datetime import datetime

from dateutil.tz import gettz


def get_current_date_in_jst() -> str:
  """Get the current date in Japan Standard Time (JST)

  Returns:
    str: The current date in the format of %Y年%m月%d日
  """
  jst = gettz("Asia/Tokyo")
  return datetime.now(tz=jst)
