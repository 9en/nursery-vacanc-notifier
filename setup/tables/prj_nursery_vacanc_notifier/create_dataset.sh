#!/bin/sh

# 環境変数を読み込む
. ../../../.env

# 1階層上のディレクトリ名を取得
DATASET_NAME=$(basename "$PWD")

# STGデータセット
bq mk --dataset \
  --force \
  --location=asia-northeast1 \
  --description="保育園の空き状況に関するデータを格納する" \
  --storage_billing_model=PHYSICAL \
  --use_legacy_sql=false \
  ${ENV_GCP_PROJECT_ID_STG}:${DATASET_NAME}

# PRDデータセット
bq mk --dataset \
  --force \
  --location=asia-northeast1 \
  --description="保育園の空き状況に関するデータを格納する" \
  --storage_billing_model=PHYSICAL \
  --use_legacy_sql=false \
  ${ENV_GCP_PROJECT_ID}:${DATASET_NAME}
