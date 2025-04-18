# Variáveis
PYTHON_VERSION := 3.12
PYENV := $(shell which pyenv 2> /dev/null)
VENV := venv
BIN := $(VENV)/bin
PIPX := pipx

# Verificar pipx
.PHONY: check-pipx
check-pipx:
	@echo "Verificando instalação do pipx..."
	@if command -v pipx > /dev/null; then \
		echo "pipx encontrado em: $$(which pipx)"; \
	else \
		echo "pipx não encontrado. Instalando..."; \
		python3 -m pip install --user pipx; \
		python3 -m pipx ensurepath; \
		echo "Instalação do pipx concluída."; \
		echo "Para continuar agora, execute: export PATH=$$HOME/.local/bin:$$PATH"; \
		export PATH=~/.local/bin:$$PATH; \
	fi

# Verificar Python
.PHONY: check-python
check-python:
	@echo "Verificando instalação do Python $(PYTHON_VERSION)..."
ifdef PYENV
	@echo "pyenv encontrado em: $(PYENV)"
	
	# Verificar se a versão está instalada
	@if $(PYENV) versions | grep -q $(PYTHON_VERSION); then \
		echo "Python $(PYTHON_VERSION) já está instalado via pyenv"; \
	else \
		echo "Python $(PYTHON_VERSION) não encontrado. Instalando..."; \
		$(PYENV) install $(PYTHON_VERSION); \
	fi
	
	# Configurar a versão local
	$(PYENV) local $(PYTHON_VERSION)
	
	@echo "Python $(PYTHON_VERSION) configurado via pyenv"
else
	@echo "pyenv não encontrado. Verificando Python do sistema..."
	
	@if command -v python$(PYTHON_VERSION) > /dev/null; then \
		echo "Python $(PYTHON_VERSION) encontrado no sistema"; \
		PYTHON_CMD=python$(PYTHON_VERSION); \
	elif command -v python3 > /dev/null; then \
		PYVER=$$(python3 --version 2>&1 | cut -d" " -f2); \
		PYMAJOR=$$(echo $$PYVER | cut -d. -f1-2); \
		echo "Python $$PYVER encontrado no sistema"; \
		if [ "$$PYMAJOR" = "$(PYTHON_VERSION)" ]; then \
			echo "Versão compatível com $(PYTHON_VERSION)"; \
			PYTHON_CMD=python3; \
		else \
			echo "AVISO: A versão do Python ($$PYMAJOR) é diferente de $(PYTHON_VERSION)"; \
			echo "Continuando mesmo assim com python3"; \
			PYTHON_CMD=python3; \
		fi; \
	else \
		echo "ERRO: Nenhuma versão do Python encontrada no sistema"; \
		echo "Por favor, instale Python $(PYTHON_VERSION) ou pyenv"; \
		exit 1; \
	fi
endif

# Alvos padrão
.PHONY: all
all: install

# Criar ambiente virtual
$(VENV): check-python
	@if command -v $(PYENV) > /dev/null && [ -f .python-version ]; then \
		PYTHON_CMD=$$($(PYENV) which python); \
		echo "Criando ambiente virtual com Python do pyenv: $$PYTHON_CMD"; \
		$$PYTHON_CMD -m venv $(VENV); \
	elif command -v python$(PYTHON_VERSION) > /dev/null; then \
		echo "Criando ambiente virtual com python$(PYTHON_VERSION)"; \
		python$(PYTHON_VERSION) -m venv $(VENV); \
	else \
		echo "Criando ambiente virtual com python3"; \
		python3 -m venv $(VENV); \
	fi
	$(BIN)/pip install --upgrade pip

# Instalar dependências
.PHONY: deps
deps: $(VENV)
	$(BIN)/pip install --no-cache-dir -r requirements.txt
	$(BIN)/pip install --no-cache-dir -e .

# Preparar diretórios
.PHONY: prepare
prepare:
	mkdir -p src/edlab_filemanager.egg-info
	chmod -R 777 src/edlab_filemanager.egg-info

# Instalar com pip no lugar de pipx
.PHONY: install-pip
install-pip: deps prepare
	@echo "Instalando com pip em vez de pipx..."
	$(BIN)/pip install -e .
	@echo "Instalado! Execute com: $(VENV)/bin/edlab-filemanager"

# Instalar globalmente via pipx
.PHONY: install
install: deps prepare check-pipx
	@echo "Removendo instalações anteriores..."
	-$(PIPX) uninstall edlab-filemanager > /dev/null 2>&1 || true
	-rm -rf ~/.local/share/pipx/venvs/edlab-filemanager > /dev/null 2>&1 || true
	@echo "Instalando com pipx..."
	$(PIPX) install --verbose --force . || $(MAKE) install-pip

# Desinstalar
.PHONY: uninstall
uninstall: check-pipx
	-$(PIPX) uninstall edlab-filemanager > /dev/null 2>&1 || true
	@echo "Tentando remover symlink manualmente se existir..."
	-rm -f /usr/local/bin/edlab-filemanager > /dev/null 2>&1 || true
	-rm -f ~/.local/bin/edlab-filemanager > /dev/null 2>&1 || true

# Limpar arquivos temporários
.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf build/
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf ~/.cache/pip

# Reinstalar
.PHONY: reinstall
reinstall: uninstall clean install