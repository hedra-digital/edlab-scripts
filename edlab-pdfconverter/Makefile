# Makefile para identificar o sistema operacional e copiar o arquivo edlab-pdfconverter.py para a pasta bin
# Além disso, cria um link simbólico sem a extensão .py e assegura permissões de execução

# Definir a variável de sistema
OS := $(shell uname -s)
INSTALL_DIR := $(HOME)/bin
FILE_TO_INSTALL := edlab-pdfconverter.py
LINK_NAME := edlab-pdfconverter

# Verificar o sistema operacional
DISTRO := unknown
ifeq ($(OS), Linux)
	# Checar a distribuição Linux
	ifneq ($(shell grep -i manjaro /etc/os-release),)
		DISTRO := manjaro
	else ifneq ($(shell grep -i ubuntu /etc/os-release),)
		DISTRO := ubuntu
	endif
else ifeq ($(OS), Darwin)
	DISTRO := macos
endif

.PHONY: install

install:
	@echo "Detectado: $(DISTRO)"
	# Criar o diretório bin se não existir
	@mkdir -p $(INSTALL_DIR)

	# Comandos específicos por sistema operacional
	@if [ "$(DISTRO)" = "manjaro" ]; then \
		echo "Instalando em Manjaro"; \
		cp $(FILE_TO_INSTALL) $(INSTALL_DIR)/; \
		chmod +x $(INSTALL_DIR)/$(FILE_TO_INSTALL); \
		ln -sf $(INSTALL_DIR)/$(FILE_TO_INSTALL) $(INSTALL_DIR)/$(LINK_NAME); \
	elif [ "$(DISTRO)" = "ubuntu" ]; then \
		echo "Instalando em Ubuntu"; \
		cp $(FILE_TO_INSTALL) $(INSTALL_DIR)/; \
		chmod +x $(INSTALL_DIR)/$(FILE_TO_INSTALL); \
		ln -sf $(INSTALL_DIR)/$(FILE_TO_INSTALL) $(INSTALL_DIR)/$(LINK_NAME); \
	elif [ "$(DISTRO)" = "macos" ]; then \
		echo "Instalando em macOS"; \
		cp $(FILE_TO_INSTALL) $(INSTALL_DIR)/; \
		chmod +x $(INSTALL_DIR)/$(FILE_TO_INSTALL); \
		ln -sf $(INSTALL_DIR)/$(FILE_TO_INSTALL) $(INSTALL_DIR)/$(LINK_NAME); \
	else \
		echo "Sistema não suportado"; \
	fi

	@echo "Instalação concluída em $(INSTALL_DIR)"
	@echo "Use o comando '$(LINK_NAME)' para executar o script"
	@echo "Certifique-se de que $(INSTALL_DIR) está no PATH"
