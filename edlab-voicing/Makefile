# Variáveis
PYTHON_VERSION := 3.12
PYENV := $(shell command -v pyenv 2> /dev/null)
PYTHON := python$(PYTHON_VERSION)
VENV := venv
BIN := $(VENV)/bin
PIPX := pipx

# Verificar pyenv e Python 3.12
.PHONY: check-python
check-python:
	@echo "Verificando instalação do pyenv e Python $(PYTHON_VERSION)..."
ifdef PYENV
	@echo "pyenv encontrado em: $(PYENV)"
	@if pyenv versions | grep -q $(PYTHON_VERSION); then \
		echo "Python $(PYTHON_VERSION) já está instalado via pyenv"; \
		pyenv local $(PYTHON_VERSION); \
		echo "Python $(PYTHON_VERSION) ativado para este projeto"; \
	else \
		echo "Python $(PYTHON_VERSION) não encontrado. Instalando..."; \
		pyenv install $(PYTHON_VERSION); \
		pyenv local $(PYTHON_VERSION); \
		echo "Python $(PYTHON_VERSION) instalado e ativado para este projeto"; \
	fi
else
	@echo "pyenv não encontrado. Por favor instale pyenv primeiro."
	@echo "Veja instruções em: https://github.com/pyenv/pyenv#installation"
	@exit 1
endif
	@echo "Versão Python ativa: $$(python --version)"

# Alvos padrão
.PHONY: all
all: install

# Criar ambiente virtual
$(VENV): check-python
	$$(pyenv which python) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip

# Instalar dependências
.PHONY: deps
deps: $(VENV)
	$(BIN)/pip install -r requirements.txt

# Preparar diretórios
.PHONY: prepare
prepare:
	mkdir -p src/voicing.egg-info
	chmod -R 777 src/voicing.egg-info

# Instalar globalmente
.PHONY: install
install: deps prepare
	$(PIPX) uninstall voicing || true
	rm -rf ~/.local/share/pipx/venvs/voicing || true
	$(PIPX) install -e . --force
	
# Desinstalar
.PHONY: uninstall
uninstall:
	$(PIPX) uninstall voicing || true

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