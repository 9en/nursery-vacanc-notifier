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
		$(PROJECT_NAME)

.PHONY: exec
exec:
	@docker exec -it $(PROJECT_NAME) /bin/bash

.PHONY: stop
stop:
	@docker stop $(PROJECT_NAME)

.PHONY: local_prd
local_prd:
	@docker exec -it \
		--env ENV_FOR_DYNACONF=production \
		$(PROJECT_NAME) \
		curl -X GET localhost:8080

.PHONY: local_dev
local_dev:
	@docker exec -it \
		--env ENV_FOR_DYNACONF=development \
		$(PROJECT_NAME) \
		curl -X GET localhost:8080

.PHONY: logs
logs:
	@docker logs $(PROJECT_NAME)
