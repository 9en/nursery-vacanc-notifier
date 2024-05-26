import os

import pandas as pd
from google.cloud import bigquery
from utils.dynaconf import get_config_value
from utils.gcp import bq_df_load_job, bq_query_job


class BigQueryJob:
  """BigQuery ジョブを管理するクラス。指定された日付のパーティションに対して削除またはドライランクエリを実行します。

  Attributes:
    client (bigquery.Client): BigQuery クライアント。
    update_date (str): 更新日付 (形式: 'YYYY-MM-DD')。
    project_id (str): プロジェクトID。
    dataset_name (str): データセット名。
    table_name (str): テーブル名。
  """

  def __init__(self) -> None:
    """BigQueryJob クラスのコンストラクタ。

    Args:
        update_date (str): 更新日付 (形式: 'YYYY-MM-DD')。
    """
    self.project_id = os.getenv("ENV_GCP_PROJECT_ID")
    self.dataset_name = f"prj_{get_config_value('PROJECT_NAME')}".replace("-", "_")
    self.table_name = "raw_nursery_vacanc"
    self.client = bigquery.Client(project=self.project_id)

  def run_query(self, query_type: str, update_date: str) -> None:
    """指定されたクエリタイプに応じてクエリを実行します。

    Args:
      query_type (str): クエリタイプ ("delete" または "dry_run")。
      update_date (str): 更新日付 (形式: 'YYYY-MM-DD')。

    Raises:
      ValueError: 無効なクエリタイプが指定された場合。

    Returns:
      Optional[int]: スキャンされるバイト数（ドライランの場合）。削除の場合は None。
    """
    if query_type not in ["delete", "dry_run"]:
      msg = "Invalid query type. Must be 'delete' or 'dry_run'."
      raise ValueError(msg)
    return bq_query_job(
      query_type,
      self.client,
      update_date,
      self.project_id,
      self.dataset_name,
      self.table_name,
    )

  def load(self, df: pd.DataFrame) -> None:
    """DataFrame を BigQuery テーブルにロードします。

    Args:
      df (pd.DataFrame): ロードするデータ。
    """
    bq_df_load_job(self.client, df, self.project_id, self.dataset_name, self.table_name)
