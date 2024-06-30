#!/bin/bash

read -p "GCPプロジェクトID（prd）を入力してください: " ENV_GCP_PROJECT_ID
read -p "GCPプロジェクトID（stg）を入力してください: " ENV_GCP_PROJECT_ID_STG

echo ENV_GCP_PROJECT_ID=$ENV_GCP_PROJECT_ID > .env.secret
echo ENV_GCP_PROJECT_ID_STG=$ENV_GCP_PROJECT_ID_STG >> .env.secret
