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
		--env ENV_GCP_PROJECT_ID=$(ENV_GCP_PROJECT_ID_STG) \
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
		--memory=512 \
		--timeout=60 \
		--source=function/ \
		--entry-point=main \
		--no-allow-unauthenticated \
		--project=$(ENV_GCP_PROJECT_ID) \
		--set-env-vars=ENV_FOR_DYNACONF=$(ENV_FOR_DYNACONF),ENV_LOGGER=$(ENV_LOGGER_CLOUD),ENV_GCP_PROJECT_ID=$(ENV_GCP_PROJECT_ID) \
		--service-account=$(PROJECT_NAME)@$(ENV_GCP_PROJECT_ID).iam.gserviceaccount.com

.PHONY: deploy_stg
deploy_stg: deploy_requirements
	@gcloud functions deploy $(PROJECT_NAME) \
		--gen2 \
		--trigger-http \
		--region=asia-northeast1 \
		--runtime=python311 \
		--memory=512 \
		--timeout=60 \
		--source=function/ \
		--entry-point=main \
		--no-allow-unauthenticated \
		--project=$(ENV_GCP_PROJECT_ID_STG) \
		--set-env-vars=ENV_FOR_DYNACONF=$(ENV_FOR_DYNACONF_STG),ENV_LOGGER=$(ENV_LOGGER_CLOUD),ENV_GCP_PROJECT_ID=$(ENV_GCP_PROJECT_ID_STG) \
		--service-account=$(PROJECT_NAME)@$(ENV_GCP_PROJECT_ID_STG).iam.gserviceaccount.com

.PHONY: deploy_prd_env
deploy_prd_env:
	@gcloud functions describe $(PROJECT_NAME) \
		--project=$(ENV_GCP_PROJECT_ID) \
		--region=asia-northeast1 \
		--format=json \
		| jq '.serviceConfig.environmentVariables'

.PHONY: deploy_stg_env
deploy_stg_env:
	@gcloud functions describe $(PROJECT_NAME) \
		--project=$(ENV_GCP_PROJECT_ID_STG) \
		--region=asia-northeast1 \
		--format=json \
		| jq '.serviceConfig.environmentVariables'

.PHONY: scheduler_prd
scheduler_prd:
	@if gcloud scheduler jobs describe $(PROJECT_NAME)-scheduler --project=$(ENV_GCP_PROJECT_ID) --location=asia-northeast1 > /dev/null 2>&1; then \
		opt="update"; \
	else \
		opt="create"; \
	fi; \
	gcloud scheduler jobs $${opt} http $(PROJECT_NAME)-scheduler \
		--schedule="5 0-11 25 * *" \
		--uri="https://asia-northeast1-$(ENV_GCP_PROJECT_ID).cloudfunctions.net/$(PROJECT_NAME)" \
		--http-method=GET \
		--time-zone=Asia/Tokyo \
		--location=asia-northeast1 \
		--project=$(ENV_GCP_PROJECT_ID) \
		--description="${PROJECT_NAME} scheduler" \
		--oidc-service-account-email=$(PROJECT_NAME)@$(ENV_GCP_PROJECT_ID).iam.gserviceaccount.com \
		--oidc-token-audience="https://asia-northeast1-$(ENV_GCP_PROJECT_ID).cloudfunctions.net/$(PROJECT_NAME)"

.PHONY: scheduler_stg
scheduler_stg:
	@if gcloud scheduler jobs describe $(PROJECT_NAME)-scheduler --project=$(ENV_GCP_PROJECT_ID_STG) --location=asia-northeast1 > /dev/null 2>&1; then \
		opt="update"; \
	else \
		opt="create"; \
	fi; \
	gcloud scheduler jobs $${opt} http $(PROJECT_NAME)-scheduler \
		--schedule="5 0-11 25 * *" \
		--uri="https://asia-northeast1-$(ENV_GCP_PROJECT_ID_STG).cloudfunctions.net/$(PROJECT_NAME)" \
		--http-method=GET \
		--time-zone=Asia/Tokyo \
		--location=asia-northeast1 \
		--project=$(ENV_GCP_PROJECT_ID_STG) \
		--description="${PROJECT_NAME} scheduler" \
		--oidc-service-account-email=$(PROJECT_NAME)@$(ENV_GCP_PROJECT_ID_STG).iam.gserviceaccount.com \
		--oidc-token-audience="https://asia-northeast1-$(ENV_GCP_PROJECT_ID_STG).cloudfunctions.net/$(PROJECT_NAME)"

.PHONY: func_logs
func_logs:
	@gcloud functions logs read $(PROJECT_NAME) \
		--region=asia-northeast1 \
		--project=$(ENV_GCP_PROJECT_ID_STG)

.PHONY: logs
logs:
	@docker logs $(PROJECT_NAME)
