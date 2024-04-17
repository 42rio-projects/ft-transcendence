COMPOSE = cd compose && cd src && docker-compose -f docker-compose.yml

VOLUMES = ../postgres_data

all: up

up: volumes
	$(COMPOSE) up -d --build

start:
	$(COMPOSE) start

down:
	$(COMPOSE) down

re:
	$(COMPOSE) down
	$(COMPOSE) up

stop:
	$(COMPOSE) stop

restart:
	$(COMPOSE) restart

logs:
	$(COMPOSE) logs -f

volumes:
	mkdir -p $(VOLUMES)

clean: down
	-docker rm -f $$(docker ps -aq)
	-docker rmi -f $$(docker images -aq)
	-docker volume rm -f $$(docker volume ls -q)
	-docker network rm -f $$(docker network ls -q)

.PHONY: all up start down stop restart logs volumes clean
