#!/bin/sh

# 環境変数を読み込む
. ../../../../.env

TABLE_NAME=$(basename "$PWD")
DATASET_NAME=$(basename $(dirname "$PWD"))
DESCRIPTION="保育園の空き状況に関するデータを格納する"

# STGデータセット
bq rm -f ${ENV_GCP_PROJECT_ID_STG}:${DATASET_NAME}.${TABLE_NAME}
bq mk --table \
  --time_partitioning_type DAY \
  --time_partitioning_field dt \
  --schema=./schema.json \
  --require_partition_filter \
  --description=${DESCRIPTION} \
  ${ENV_GCP_PROJECT_ID_STG}:${DATASET_NAME}.${TABLE_NAME}

# PRDデータセット
bq rm -f ${ENV_GCP_PROJECT_ID}:${DATASET_NAME}.${TABLE_NAME}
bq mk --table \
  --time_partitioning_type DAY \
  --time_partitioning_field dt \
  --schema=./schema.json \
  --require_partition_filter \
  --description=${DESCRIPTION} \
  ${ENV_GCP_PROJECT_ID}:${DATASET_NAME}.${TABLE_NAME}
