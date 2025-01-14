import sqlite3
import hashlib
import logging
from contextlib import contextmanager
from config import DB_PATH

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Exceção personalizada para erros de banco de dados"""
    pass

@contextmanager
def get_db_connection():
    """Gerenciador de contexto para conexões do banco de dados"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro no banco de dados: {str(e)}")
        raise DatabaseError(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if conn:
            conn.close()

def update_users_table():
    """Atualiza a estrutura da tabela users"""
    try:
        logger.info("Iniciando atualização da tabela users")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Backup dos dados existentes
            cursor.execute("SELECT id, username, password FROM users")
            existing_users = cursor.fetchall()
            
            # Dropar a tabela antiga
            cursor.execute("DROP TABLE IF EXISTS users")
            
            # Criar nova tabela com estrutura atualizada
            cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                user_type TEXT CHECK(user_type IN ('admin', 'user')) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Restaurar dados com valores padrão para novos campos
            for user in existing_users:
                cursor.execute("""
                    INSERT INTO users (id, username, email, password, user_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (user[0], user[1], f"{user[1]}@example.com", user[2], "user"))
            
            logger.info("Tabela users atualizada com sucesso")
            
    except Exception as e:
        logger.error(f"Erro ao atualizar tabela users: {str(e)}")
        raise DatabaseError(f"Erro ao atualizar tabela users: {str(e)}")

def update_empenhos_table():
    """Atualiza a estrutura da tabela empenhos"""
    try:
        logger.info("Iniciando atualização da tabela empenhos")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Backup dos dados existentes (se houver)
            # try:
            #     cursor.execute("""
            #         SELECT id, numero, descricao, valor 
            #         FROM empenhos
            #     """)
            #     existing_empenhos = cursor.fetchall()
            # except sqlite3.OperationalError:
            #     existing_empenhos = []
            
            # # Dropar a tabela antiga
            # cursor.execute("DROP TABLE IF EXISTS empenhos")
            
            # Criar nova tabela com estrutura atualizada
            cursor.execute('''
            CREATE TABLE empenhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_entrada TEXT NOT NULL,
                numero INTEGER NOT NULL,
                empresa TEXT NOT NULL,
                setor TEXT NOT NULL,
                numero_nota TEXT NOT NULL,
                data_nota TEXT NOT NULL,
                valor REAL NOT NULL,
                data_saida TEXT NOT NULL,
                observacao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Restaurar dados antigos com valores padrão para novos campos
            # if existing_empenhos:
            #     from datetime import datetime
            #     current_date = datetime.now().strftime("%d/%m/%Y")
                
            #     for empenho in existing_empenhos:
            #         cursor.execute("""
            #             INSERT INTO empenhos (
            #                 data_entrada, numero, empresa, setor, 
            #                 numero_nota, data_nota, valor, 
            #                 data_saida, observacao
            #             )
            #             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            #         """, (
            #             current_date,          # data_entrada
            #             empenho[1],           # numero
            #             "Empresa Anterior",   # empresa
            #             "ADMINISTRAÇÃO",      # setor
            #             "N/A",               # numero_nota
            #             current_date,         # data_nota
            #             empenho[3],          # valor
            #             current_date,         # data_saida
            #             empenho[2]           # observacao (antiga descrição)
            #         ))
                
            # logger.info("Tabela empenhos atualizada com sucesso")
            
    except Exception as ex:
        logger.error(f"Erro ao atualizar tabela empenhos: {str(ex)}")
        raise DatabaseError(f"Erro ao atualizar tabela empenhos: {str(ex)}")

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    try:
        logger.info(f"Iniciando inicialização do banco de dados em: {DB_PATH}")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar se precisa atualizar a estrutura da tabela users
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if "email" not in columns or "user_type" not in columns:
                logger.info("Atualizando estrutura da tabela users...")
                update_users_table()
            else:
                # Criação da tabela de usuários
                logger.info("Criando tabela de usuários...")
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    user_type TEXT CHECK(user_type IN ('admin', 'user')) DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

            # Verificar se já existe usuário padrão
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("natan",))
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("Adicionando usuário padrão...")
                # Adicionar usuário padrão como administrador
                hashed_password = hashlib.sha256("@31n19v01m@".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, email, password, user_type)
                    VALUES (?, ?, ?, ?)
                """, ("natan", "admin@example.com", hashed_password, "admin"))
                logger.info("Usuário padrão adicionado com sucesso")
            else:
                logger.info("Usuário padrão já existe")
            
            # Verificar se precisa atualizar a estrutura da tabela empenhos
            cursor.execute("PRAGMA table_info(empenhos)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if "empresa" not in columns or "setor" not in columns:
                logger.info("Atualizando estrutura da tabela empenhos...")
                update_empenhos_table()
            else:
                # Criação da tabela de empenhos
                logger.info("Criando tabela de empenhos...")
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS empenhos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_entrada TEXT NOT NULL,
                    numero INTEGER NOT NULL,
                    empresa TEXT NOT NULL,
                    setor TEXT NOT NULL,
                    numero_nota TEXT NOT NULL,
                    data_nota TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data_saida TEXT NOT NULL,
                    observacao TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
            
            logger.info("Banco de dados inicializado com sucesso")
            
    except Exception as e:
        logger.error(f"Erro ao inicializar o banco de dados: {str(e)}")
        raise DatabaseError(f"Erro ao inicializar o banco de dados: {str(e)}")

def validate_login(username: str, password: str) -> dict:
    """Valida as credenciais do usuário e retorna os dados do usuário"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("""
                SELECT id, username, email, user_type 
                FROM users 
                WHERE username = ? AND password = ?
            """, (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                return {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "user_type": user[3]
                }
            return None
    except Exception as e:
        logger.error(f"Erro ao validar login: {str(e)}")
        return None
