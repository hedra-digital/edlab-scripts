# Variáveis
PYTHON_VERSION := 3.12
PYENV := $(shell which pyenv 2> /dev/null)
VENV := venv
BIN := $(VENV)/bin
PIPX := pipx

# Verificar pyenv e Python 3.12
.PHONY: check-python
check-python:
	@echo "Verificando instalação do pyenv e Python $(PYTHON_VERSION)..."
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
	
	# Usar um script shell para garantir que a versão correta seja usada
	@bash -c 'source ~/.bashrc > /dev/null 2>&1 || true; \
		PYVER=$$(python3 --version 2>&1 | cut -d" " -f2); \
		PYMAJOR=$$(echo $$PYVER | cut -d. -f1-2); \
		echo "Versão Python detectada: $$PYVER ($$PYMAJOR)"; \
		if [[ "$$PYMAJOR" != "$(PYTHON_VERSION)" ]]; then \
			echo "AVISO: A versão Python $$PYMAJOR não é $(PYTHON_VERSION)"; \
			echo "Tentando usar o executável Python específico da versão $(PYTHON_VERSION)..."; \
		fi'
	
	# Assegurar que temos o caminho correto para o Python
	@PY_CMD=$(shell $(PYENV) which python 2>/dev/null || echo python3)
	@echo "Usando Python em: $$PY_CMD"
else
	@echo "pyenv não encontrado. Por favor instale pyenv primeiro."
	@echo "Veja instruções em: https://github.com/pyenv/pyenv#installation"
	@exit 1
endif

# Alvos padrão
.PHONY: all
all: install

# Criar ambiente virtual - importante: usar o Python do pyenv diretamente
$(VENV): check-python
	bash -c 'source ~/.bashrc > /dev/null 2>&1 || true; \
		if command -v $(PYENV) > /dev/null; then \
			PYTHON_CMD=$$($(PYENV) which python); \
			echo "Criando ambiente virtual com: $$PYTHON_CMD"; \
			$$PYTHON_CMD -m venv $(VENV); \
		else \
			echo "Usando Python padrão"; \
			python3 -m venv $(VENV); \
		fi'
	$(BIN)/pip install --upgrade pip

# Instalar dependências
.PHONY: deps
deps: $(VENV)
	$(BIN)/pip install -r requirements.txt

# Preparar diretórios
.PHONY: prepare
prepare:
	mkdir -p src/edlab_pdfmanager.egg-info
	chmod -R 777 src/edlab_pdfmanager.egg-info

# Instalar globalmente
.PHONY: install
install: deps prepare
	$(PIPX) uninstall edlab-pdfmanager || true
	rm -rf ~/.local/share/pipx/venvs/edlab-pdfmanager || true
	$(PIPX) install -e . --force
	
# Desinstalar
.PHONY: uninstall
uninstall:
	$(PIPX) uninstall edlab-pdfmanager || true

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