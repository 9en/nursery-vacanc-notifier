import json
import os
from typing import Optional

import pandas as pd
from google.cloud import bigquery, secretmanager
from utils.dynaconf import get_config_value


def gcp_secretmanager() -> dict:
  """秘密情報を取得する

  Returns:
    dict: 秘密情報
  """
  client = secretmanager.SecretManagerServiceClient()
  name = (
    f"projects/{os.getenv('ENV_GCP_PROJECT_ID')}/secrets/{get_config_value('SECRET_MANAGER_NAME')}/versions/latest"
  )
  response = client.access_secret_version(name=name)
  return json.loads(response.payload.data.decode("UTF-8"))


def bq_query_job(
  query_type: str, client: bigquery.Client, partition_date: str, project_id: str, dataset_name: str, table_name: str
) -> Optional[int]:
  """指定されたクエリタイプに応じてクエリを実行し、必要に応じてスキャン量を返します。

  Args:
      query_type (str): クエリタイプ ("delete" または "dry_run")。
      client (bigquery.Client): BigQuery クライアント。
      partition_date (str): パーティションの日付 (形式: 'YYYY-MM-DD')。
      project_id (str): プロジェクト ID。
      dataset_name (str): データセット名。
      table_name (str): テーブル名。

  Returns:
      Optional[int]: スキャンされるバイト数（ドライランの場合）。削除の場合は None。
  """
  job_config = bigquery.QueryJobConfig(
    # NOTE: クエリパラメータはテーブル名や列名を置き換えることができない
    query_parameters=[
      bigquery.ScalarQueryParameter("partition_date", "DATE", partition_date),
    ]
  )

  if query_type == "delete":
    query = f"delete from `{project_id}.{dataset_name}.{table_name}` where dt = @partition_date"
  elif query_type == "dry_run":
    query = f"select * from `{project_id}.{dataset_name}.{table_name}` where dt = @partition_date"
    job_config.dry_run = True
    job_config.use_query_cache = False
  else:
    msg = "Invalid query type. Must be 'delete' or 'dry_run'."
    raise ValueError(msg)

  query_job = client.query(query=query, job_config=job_config)
  query_job.result()

  if query_type == "dry_run":
    return query_job.total_bytes_processed
  return None


def bq_df_load_job(
  client: bigquery.Client,
  df: pd.DataFrame,
  project_id: str,
  dataset_name: str,
  table_name: str,
) -> None:
  """Pandas DataFrame を BigQuery にロードするジョブを実行します。

  Args:
      client (bigquery.Client): BigQuery クライアント。
      df (pd.DataFrame): ロードするデータフレーム。
      schema (List[bigquery.SchemaField]): テーブルスキーマ。
      project_id (str): プロジェクトID。
      dataset_name (str): データセット名。
      table_name (str): テーブル名。
  """
  job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_APPEND",
  )
  table_id = f"{project_id}.{dataset_name}.{table_name}"
  job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
  job.result()

