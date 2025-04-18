# Variáveis
PYTHON_VERSION := 3.12
PYENV := $(shell which pyenv 2> /dev/null)
VENV := venv
BIN := $(VENV)/bin
PIPX := pipx

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
	$(BIN)/pip install -r requirements.txt

# Preparar diretórios
.PHONY: prepare
prepare:
	mkdir -p src/upscaler.egg-info
	chmod -R 777 src/upscaler.egg-info

# Instalar globalmente
.PHONY: install
install: deps prepare
	$(PIPX) uninstall upscaler || true
	rm -rf ~/.local/share/pipx/venvs/upscaler || true
	$(PIPX) install -e . --force

# Desinstalar
.PHONY: uninstall
uninstall:
	$(PIPX) uninstall upscaler || true

# Limpar arquivos temporários
.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	rm -rf build/
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Reinstalar
.PHONY: reinstall
reinstall: uninstall clean install