# Variáveis
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin
PIPX := pipx

# Alvos padrão
.PHONY: all
all: install

# Criar ambiente virtual
$(VENV):
	$(PYTHON) -m venv $(VENV)
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