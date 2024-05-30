GREEN := $(shell printf "\033[32m")
YELLOW := $(shell printf "\033[33m")
BLUE := $(shell printf "\033[34m")
MAGENTA := $(shell printf "\033[35m")
RESET := $(shell printf "\033[0m")

COMPOSE = docker-compose
NAME = "FT_ENDGAME"

all: up
	@printf "\n$(GREEN)✨ Projeto $(NAME) criado com sucesso! ✨$(RESET)\n\n"
	@docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
	@printf "\n$(BLUE)📊 Recursos utilizados pelos containers: 📊$(RESET)\n\n"
	@docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

asc: ascii_art

up: ascii_art
	$(COMPOSE) up -d --build
	@printf "\n$(BLUE)🚀 Inicializando o projeto $(NAME)... 🚀$(RESET)\n\n"

verbose:
	$(COMPOSE) up
	@printf "\n$(BLUE)🚀 Inicializando o projeto $(NAME)... 🚀$(RESET)\n\n"

start:
	$(COMPOSE) start
	@printf "\n$(YELLOW)🔀 Projeto $(NAME) iniciado 🔀$(RESET)\n\n"

down: stop
	$(COMPOSE) down -v
	@printf "\n$(MAGENTA)🛑 Projeto $(NAME) parado 🛑$(RESET)\n\n"

re: down up
		@printf "\n$(YELLOW)🔁 Projeto $(NAME) recriado 🔁$(RESET)\n\n"

stop:
	$(COMPOSE) stop
	@printf "\n$(MAGENTA)⏸️ Projeto $(NAME) pausado ⏸️$(RESET)\n\n"

restart:
	$(COMPOSE) restart
		@printf "\n$(GREEN)🔁 Projeto $(NAME) recriado 🔁$(RESET)\n\n"

logs:
	$(COMPOSE) logs -f
	@printf "\n$(BLUE)🔍 Logs do projeto Projeto $(NAME) disponíveis 🔍$(RESET)\n\n"

clean:
	$(COMPOSE) down -v
	@printf "\n$(GREEN)🧹 Limpeza concluída 🧹$(RESET)\n\n"

nuke: clean
	-docker rm -f $$(docker ps -aq)
	-docker rmi -f $$(docker images -aq)
	-docker volume rm -f $$(docker volume ls -q)
	-docker network rm -f $$(docker network ls -q)
	@printf "\n$(YELLOW)💣 Apagou tudo 💣$(RESET)\n\n"


ascii_art:
	@echo "╔═══════════════════════════════════════════════════════════════╗"
	@echo "║                                                               ║"
	@echo "║                                                               ║"
	@echo "║  ██╗   ██╗██╗████████╗██╗███╗   ██╗██╗  ██╗ ██████╗           ║"
	@echo "║  ██║   ██║██║╚══██╔══╝██║████╗  ██║██║  ██║██╔═══██╗          ║"
	@echo "║  ██║   ██║██║   ██║   ██║██╔██╗ ██║███████║██║   ██║          ║"
	@echo "║  ╚██╗ ██╔╝██║   ██║   ██║██║╚██╗██║██╔══██║██║   ██║          ║"
	@echo "║   ╚████╔╝ ██║   ██║   ██║██║ ╚████║██║  ██║╚██████╔╝          ║"
	@echo "║    ╚═══╝  ╚═╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝           ║"
	@echo "║                                                               ║"
	@echo "║   ██████╗  ██████╗ ██╗   ██╗███████╗██████╗ ███████╗███████╗  ║"
	@echo "║  ██╔════╝ ██╔════╝ ██║   ██║██╔════╝██╔══██╗██╔════╝██╔════╝  ║"
	@echo "║  ██║  ███╗██║  ███╗██║   ██║█████╗  ██║  ██║█████╗  ███████╗  ║"
	@echo "║  ██║   ██║██║   ██║██║   ██║██╔══╝  ██║  ██║██╔══╝  ╚════██║  ║"
	@echo "║  ╚██████╔╝╚██████╔╝╚██████╔╝███████╗██████╔╝███████╗███████║  ║"
	@echo "║   ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚══════╝  ║"
	@echo "║                                                               ║"
	@echo "║   ██████╗  ██████╗ ██████╗ ██████╗ ██████╗ ███████╗██╗ █████╗ ║"
	@echo "║  ██╔════╝ ██╔════╝██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║██╔══██╗║"
	@echo "║  ██║  ███╗██║     ██║   ██║██████╔╝██████╔╝█████╗  ██║███████║║"
	@echo "║  ██║   ██║██║     ██║   ██║██╔══██╗██╔══██╗██╔══╝  ██║██╔══██║║"
	@echo "║  ╚██████╔╝╚██████╗╚██████╔╝██║  ██║██║  ██║███████╗██║██║  ██║║"
	@echo "║   ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═╝║"
	@echo "║                                                               ║"
	@echo "║  ██████╗ ██╗   ██╗ █████╗ ██████╗  ██████╗  █████╗ ███████╗   ║"
	@echo "║  ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔════╝ ██╔══██╗██╔════╝   ║"
	@echo "║  ██║  ██║██║   ██║███████║██████╔╝██║  ███╗███████║███████╗   ║"
	@echo "║  ██║  ██║╚██╗ ██╔╝██╔══██║██╔══██╗██║   ██║██╔══██║╚════██║   ║"
	@echo "║  ██████╔╝ ╚████╔╝ ██║  ██║██║  ██║╚██████╔╝██║  ██║███████║   ║"
	@echo "║  ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝   ║"
	@echo "║                                                               ║"
	@echo "║                                                               ║"
	@echo "╚═══════════════════════════════════════════════════════════════╝"

.PHONY: all up start down stop restart logs clean nuke clear re ascii_art
