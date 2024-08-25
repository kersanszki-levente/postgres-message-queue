DOCKER_COMPOSE=docker compose -f docker/compose.yaml

run: build
	$(DOCKER_COMPOSE) up

build: docker/.env
	$(DOCKER_COMPOSE) build

shell: build
	$(DOCKER_COMPOSE) run -it worker /bin/bash

docker/.env:
	@touch docker/.env & \
	echo "POSTGRES_HOST=postgres" >>docker/.env 2>&1 & \
	echo "POSTGRES_USER=postgres" >>docker/.env 2>&1 & \
	echo "POSTGRES_PASSWORD=secret" >>docker/.env 2>&1 & \
	echo "POSTGRES_DB=scheduling" >>docker/.env 2>&1
