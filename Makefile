include .env
PROJECT_NAME := $(shell basename $(CURDIR))


.PHONY: build
build:
	@docker build --no-cache . -t $(PROJECT_NAME)

.PHONY: rmi
rmi:
	@docker rmi $(PROJECT_NAME)

.PHONY: run
run:
	@docker run -it -d --rm \
		--name $(PROJECT_NAME) \
		--volume $(CURDIR):/app \
		--volume ~/.config/gcloud/:/root/.config/gcloud \
		--env ENV_FOR_DYNACONF=$(ENV_FOR_DYNACONF_STG) \
		--env ENV_LOGGER=$(ENV_LOGGER_LOCAL) \
		$(PROJECT_NAME)

.PHONY: exec
exec:
	@docker exec -it $(PROJECT_NAME) /bin/bash

.PHONY: stop
stop:
	@docker stop $(PROJECT_NAME)

.PHONY: local
local:
	@docker exec -it \
		$(PROJECT_NAME) \
		curl -X GET localhost:8080

.PHONY: deploy_requirements
deploy_requirements:
	@cat requirements.txt | grep -v -e ipykernel -e ruff > function/requirements.txt

.PHONY: deploy_prd
deploy_prd: deploy_requirements
	@gcloud functions deploy $(PROJECT_NAME) \
		--gen2 \
		--trigger-http \
		--region=asia-northeast1 \
		--runtime=python311 \
		--memory=256 \
		--timeout=60 \
		--source=function/ \
		--entry-point=main \
		--project=$(GCP_PROJECT_ID) \
		--set-env-vars=ENV_FOR_DYNACONF=$(ENV_FOR_DYNACONF),ENV_LOGGER=$(ENV_LOGGER_CLOUD) \
		--service-account=$(PROJECT_NAME)@$(GCP_PROJECT_ID).iam.gserviceaccount.com

.PHONY: deploy_stg
deploy_stg: deploy_requirements
	@gcloud functions deploy $(PROJECT_NAME) \
		--gen2 \
		--trigger-http \
		--region=asia-northeast1 \
		--runtime=python311 \
		--memory=256 \
		--timeout=60 \
		--source=function/ \
		--entry-point=main \
		--project=$(GCP_PROJECT_ID_STG) \
		--set-env-vars=ENV_FOR_DYNACONF=$(ENV_FOR_DYNACONF_STG),ENV_LOGGER=$(ENV_LOGGER_CLOUD) \
		--service-account=$(PROJECT_NAME)@$(GCP_PROJECT_ID_STG).iam.gserviceaccount.com

.PHONY: deploy_prd_env
deploy_prd_env:
	@gcloud functions describe $(PROJECT_NAME) \
		--project=$(GCP_PROJECT_ID) \
		--region=asia-northeast1 \
		--format=json \
		| jq '.serviceConfig.environmentVariables'

.PHONY: deploy_stg_env
deploy_stg_env:
	@gcloud functions describe $(PROJECT_NAME) \
		--project=$(GCP_PROJECT_ID_STG) \
		--region=asia-northeast1 \
		--format=json \
		| jq '.serviceConfig.environmentVariables'

.PHONY: logs
logs:
	@docker logs $(PROJECT_NAME)
