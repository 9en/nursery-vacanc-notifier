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
		$(PROJECT_NAME)

.PHONY: exec
exec:
	@docker exec -it $(PROJECT_NAME) /bin/bash

.PHONY: stop
stop:
	@docker stop $(PROJECT_NAME)

.PHONY: logs
logs:
	@docker logs $(PROJECT_NAME)
