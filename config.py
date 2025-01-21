import os

# Configurações do Banco de Dados
DB_NAME = 'empenhos.db'
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)

# Configurações da Interface
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Sistema de Empenhos"

# Configurações de Tema
THEME_MODE = "light"
PRIMARY_COLOR = "blue"
SECONDARY_COLOR = "light_blue"

# Configurações de Logging
LOG_FILE = "app.log"
LOG_LEVEL = "INFO"

# Configurações de Validação
MAX_DESCRICAO_LENGTH = 500
MIN_VALOR = 0.01

# Configurações de arquivos estáticos
STATIC_DIR = "static_files"
PDF_DIR = os.path.join(STATIC_DIR, "pdf_exports")
EXCEL_DIR = os.path.join(STATIC_DIR, "exports")