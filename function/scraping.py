import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser, tz
from utils.dynaconf import get_config_value


def read_html_tables(html_source: bytes) -> pd.DataFrame:
  """HTMLを読み込んでDataFrameに変換する

  Args:
    html_source (bytes): HTMLソース

  Returns:
    pd.DataFrame: 変換後のDataFrame
  """
  df = pd.read_html(html_source)[0]
  df.drop([0, 1], inplace=True)
  df.columns = ["名称1", "名称", "定員", "0歳児", "1歳児", "2歳児", "3歳児", "4歳児", "5歳児"]

  # 名称を結合して、不要な列を削除
  df["名称"] = df["名称"] + "(定員:" + df["定員"] + ")"
  df.drop(["名称1", "定員"], axis=1, inplace=True)

  # 空き状況の記号を文字列に変換
  df = df.replace(get_config_value("AVAILABILITY"))

  # フォーマット変更
  df = df.melt(id_vars=["名称"], var_name="年齢", value_name="空き")
  df = df[df["空き"].isin(get_config_value("TARGET_AVAILABILITY"))]
  return df[df["年齢"].isin(get_config_value("TARGET_AGE"))]


def parse_update_time(timestamp_str: str) -> str:
  """文字列を解析してフォーマットする

  Args:
    timestamp_str (str): 時刻文字列

  Returns:
    str: 時刻文字列(%Y-%m-%d %H:%M:%S)
  """
  timestamp = parser.parse(timestamp_str)
  timestamp = timestamp.astimezone(tz.tzutc())
  return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def extract_update_time(html_source: bytes) -> str:
  """Update timeを抽出する

  Args:
    html_source (bytes): HTMLソース

  Returns:
    str: update time in the format of %Y-%m-%d %H:%M:%S
  """
  soup = BeautifulSoup(html_source, "html.parser")
  meta_tag = soup.find("meta", attrs={"name": "nsls:timestamp"})
  timestamp_str = meta_tag["content"] if meta_tag else "Tag not found"
  return parse_update_time(timestamp_str)


def scrape() -> (pd.DataFrame, str):
  """Webサイトから情報を取得する

  Returns:
      pd.DataFrame: DataFrame
      str: update time in the format of %Y-%m-%d %H:%M:%S
  """
  for city in get_config_value("REQUEST_URL"):
    html_source = requests.get(get_config_value("REQUEST_URL")[city], timeout=10)
    update_time = extract_update_time(html_source.text)
    df = read_html_tables(html_source.content)
  return df, update_time
