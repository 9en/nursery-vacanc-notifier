import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser, tz
from utils.dynaconf import get_config_value


def read_html_tables(html_source: bytes, city: str, update_date: str) -> pd.DataFrame:
  """HTMLを読み込んでDataFrameに変換する

  Args:
    html_source (bytes): HTMLソース
    city (str): 都市名
    update_date (str): 更新日

  Returns:
    pd.DataFrame: 変換後のDataFrame
  """
  df = pd.read_html(html_source)[0]
  df.drop([0, 1], inplace=True)
  df.columns = ["nursery_name1", "nursery_name", "capacity", "0歳児", "1歳児", "2歳児", "3歳児", "4歳児", "5歳児"]

  # 不要な列を削除
  df.drop(["nursery_name1"], axis=1, inplace=True)

  # 空き状況の記号を文字列に変換
  df = df.replace(get_config_value("AVAILABILITY"))

  # フォーマット変更
  df = df.melt(id_vars=["nursery_name", "capacity"], var_name="age", value_name="vacancy")
  df["city"] = city
  df["dt"] = pd.to_datetime(update_date)
  df["capacity"] = df["capacity"].astype("int64")
  return df[["dt", "city", "nursery_name", "capacity", "age", "vacancy"]]


def parse_update_date(timestamp_str: str) -> str:
  """文字列を解析してフォーマットする

  Args:
    timestamp_str (str): 時刻文字列

  Returns:
    str: 時刻文字列(%Y-%m-%d)
  """
  timestamp = parser.parse(timestamp_str)
  timestamp = timestamp.astimezone(tz.tzutc())
  return timestamp.strftime("%Y-%m-%d")


def extract_update_date(html_source: bytes) -> str:
  """Update timeを抽出する

  Args:
    html_source (bytes): HTMLソース

  Returns:
    str: update time in the format of %Y-%m-%d
  """
  soup = BeautifulSoup(html_source, "html.parser")
  meta_tag = soup.find("meta", attrs={"name": "nsls:timestamp"})
  timestamp_str = meta_tag["content"] if meta_tag else "Tag not found"
  return parse_update_date(timestamp_str)


def scrape() -> (pd.DataFrame, str):
  """Webサイトから情報を取得する

  Returns:
      pd.DataFrame: DataFrame
      str: update time in the format of %Y-%m-%d
  """
  for city in get_config_value("REQUEST_URL"):
    html_source = requests.get(get_config_value("REQUEST_URL")[city], timeout=10)
    update_date = extract_update_date(html_source.text)
    df = read_html_tables(html_source.content, city, update_date)
  return df, update_date
