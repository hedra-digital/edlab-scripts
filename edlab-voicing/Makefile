# Variáveis
PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

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

# Instalar globalmente
.PHONY: install
install: deps
	sudo $(BIN)/pip install -e .

# Desinstalar
.PHONY: uninstall
uninstall:
	sudo pip uninstall -y voicing

# Limpar arquivos temporários
.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Reinstalar
.PHONY: reinstall
reinstall: uninstall clean install
