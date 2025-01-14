import flet as ft
import logging
from database import get_db_connection
import hashlib
from assets.styles import get_styles
import sqlite3

logger = logging.getLogger(__name__)

class UserView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.styles = get_styles()
        self.editing_id = None
        self.init_ui()

    def build(self):
        """Constrói a interface do usuário"""
        return ft.Column(
            controls=[
                ft.Text("Gerenciamento de Usuários", size=30, weight=ft.FontWeight.BOLD),
                
                # Formulário de cadastro
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Cadastro de Usuário", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                controls=[
                                    self.username,
                                    self.email,
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.password,
                                    self.confirm_password,
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.user_type,
                                ]
                            ),
                            ft.Row(
                                controls=[
                                    self.save_button,
                                    self.clear_button,
                                ]
                            ),
                        ],
                        spacing=20
                    ),
                    padding=20,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                    border_radius=10,
                ),

                # Área de pesquisa
                ft.Row(
                    controls=[
                        self.search_field,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                # Tabela de usuários
                ft.Text("Usuários Cadastrados", size=20, weight=ft.FontWeight.BOLD),
                self.data_table
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )

    def init_ui(self):
        """Inicializa os componentes da interface"""
        styles = self.styles["text_field"]

        # Campo de pesquisa
        self.search_field = ft.TextField(
            label="Pesquisar usuários",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_change=self.filter_users
        )

        # Campos do formulário
        self.username = ft.TextField(
            label="Username",
            width=styles["width"],
            border_color=styles["border_color"]
        )

        self.email = ft.TextField(
            label="Email",
            width=styles["width"],
            border_color=styles["border_color"]
        )

        self.password = ft.TextField(
            label="Senha",
            width=styles["width"],
            password=True,
            can_reveal_password=True,
            border_color=styles["border_color"]
        )

        self.confirm_password = ft.TextField(
            label="Confirmar Senha",
            width=styles["width"],
            password=True,
            can_reveal_password=True,
            border_color=styles["border_color"]
        )

        self.user_type = ft.Dropdown(
            label="Tipo de Usuário",
            width=styles["width"],
            options=[
                ft.dropdown.Option("user", "Usuário"),
                ft.dropdown.Option("admin", "Administrador"),
            ],
            border_color=styles["border_color"]
        )

        # Botões
        self.save_button = ft.ElevatedButton(
            text="Salvar",
            icon=ft.icons.SAVE,
            on_click=self.add_user
        )

        self.clear_button = ft.ElevatedButton(
            text="Limpar",
            icon=ft.icons.CLEAR,
            on_click=lambda _: self.clear_fields()
        )

        # Tabela de usuários
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Username")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Data Cadastro")),
                ft.DataColumn(ft.Text("Ações")),
            ],
            rows=[]
        )

        # Carrega os usuários iniciais
        self.load_users()

    def clear_fields(self):
        """Limpa os campos do formulário"""
        self.editing_id = None
        self.username.value = ""
        self.email.value = ""
        self.password.value = ""
        self.confirm_password.value = ""
        self.user_type.value = None
        self.save_button.text = "Salvar"
        self.update()

    def filter_users(self, e):
        """Filtra os usuários com base no texto de pesquisa"""
        self.load_users(e.control.value)

    def show_error(self, message: str):
        """Exibe uma mensagem de erro"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.RED_400,
                duration=3000
            )
        )

    def show_success(self, message: str):
        """Exibe uma mensagem de sucesso"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.GREEN_400,
                duration=3000
            )
        )

    def validate_inputs(self) -> bool:
        """Valida os campos de entrada"""
        if not self.username.value:
            self.show_error("Username é obrigatório")
            return False
            
        if not self.email.value:
            self.show_error("Email é obrigatório")
            return False
            
        if not self.editing_id and not self.password.value:
            self.show_error("Senha é obrigatória")
            return False
            
        if self.password.value and self.password.value != self.confirm_password.value:
            self.show_error("As senhas não conferem")
            return False
            
        if not self.user_type.value:
            self.show_error("Tipo de usuário é obrigatório")
            return False
            
        return True

    def load_users(self, search_term=None):
        """Carrega os usuários do banco de dados"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if search_term:
                    query = """
                        SELECT id, username, email, user_type, created_at 
                        FROM users 
                        WHERE username LIKE ? OR email LIKE ?
                        ORDER BY username
                    """
                    search_pattern = f"%{search_term}%"
                    cursor.execute(query, (search_pattern, search_pattern))
                else:
                    cursor.execute("""
                        SELECT id, username, email, user_type, created_at 
                        FROM users 
                        ORDER BY username
                    """)
                
                users = cursor.fetchall()

            # Limpa as linhas existentes
            self.data_table.rows.clear()

            # Adiciona os usuários à tabela
            for user in users:
                self.data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(user["username"])),
                            ft.DataCell(ft.Text(user["email"])),
                            ft.DataCell(ft.Text(user["user_type"])),
                            ft.DataCell(ft.Text(user["created_at"])),
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_color=ft.colors.BLUE,
                                            tooltip="Editar",
                                            data=user["id"],
                                            on_click=self.edit_user
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_color=ft.colors.RED,
                                            tooltip="Excluir",
                                            data=user["id"],
                                            on_click=self.delete_user
                                        ),
                                    ]
                                )
                            ),
                        ]
                    )
                )

            self.update()

        except Exception as e:
            logger.error(f"Erro ao carregar usuários: {str(e)}")
            self.show_error("Erro ao carregar usuários")

    def edit_user(self, e):
        """Carrega os dados do usuário para edição"""
        try:
            user_id = e.control.data
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, user_type 
                    FROM users 
                    WHERE id = ?
                """, (user_id,))
                user = cursor.fetchone()

            if user:
                self.editing_id = user_id
                self.username.value = user["username"]
                self.email.value = user["email"]
                self.user_type.value = user["user_type"]
                self.password.value = ""  # Limpa o campo de senha
                self.confirm_password.value = ""  # Limpa a confirmação de senha
                self.save_button.text = "Atualizar"
                self.update()

        except Exception as e:
            logger.error(f"Erro ao carregar usuário para edição: {str(e)}")
            self.show_error("Erro ao carregar usuário para edição")

    def delete_user(self, e):
        """Exclui um usuário"""
        try:
            user_id = e.control.data
            
            # Verifica se não é o último usuário admin
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_type FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                
                if user and user["user_type"] == "admin":
                    cursor.execute("SELECT COUNT(*) as count FROM users WHERE user_type = 'admin'")
                    admin_count = cursor.fetchone()["count"]
                    
                    if admin_count <= 1:
                        self.show_error("Não é possível excluir o último usuário administrador")
                        return
            
            def confirm_delete(e):
                if e.control.data:
                    try:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                        self.show_success("Usuário excluído com sucesso!")
                        self.load_users()
                    except Exception as ex:
                        logger.error(f"Erro ao excluir usuário: {str(ex)}")
                        self.show_error("Erro ao excluir usuário")
                dlg.open = False
                self.page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar exclusão"),
                content=ft.Text("Tem certeza que deseja excluir este usuário?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=confirm_delete, data=False),
                    ft.TextButton("Excluir", on_click=confirm_delete, data=True),
                ],
            )
            
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        except Exception as e:
            logger.error(f"Erro ao excluir usuário: {str(e)}")
            self.show_error("Erro ao excluir usuário")

    def add_user(self, e):
        """Adiciona ou atualiza um usuário"""
        try:
            if not self.validate_inputs():
                return

            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if self.editing_id:
                    # Atualização de usuário
                    if self.password.value:  # Se forneceu nova senha
                        hashed_password = hashlib.sha256(self.password.value.encode()).hexdigest()
                        cursor.execute("""
                            UPDATE users 
                            SET username = ?, email = ?, password = ?, user_type = ?
                            WHERE id = ?
                        """, (
                            self.username.value,
                            self.email.value,
                            hashed_password,
                            self.user_type.value,
                            self.editing_id
                        ))
                    else:  # Mantém a senha atual
                        cursor.execute("""
                            UPDATE users 
                            SET username = ?, email = ?, user_type = ?
                            WHERE id = ?
                        """, (
                            self.username.value,
                            self.email.value,
                            self.user_type.value,
                            self.editing_id
                        ))
                    self.show_success("Usuário atualizado com sucesso!")
                else:
                    # Novo usuário
                    hashed_password = hashlib.sha256(self.password.value.encode()).hexdigest()
                    cursor.execute("""
                        INSERT INTO users (username, email, password, user_type)
                        VALUES (?, ?, ?, ?)
                    """, (
                        self.username.value,
                        self.email.value,
                        hashed_password,
                        self.user_type.value
                    ))
                    self.show_success("Usuário cadastrado com sucesso!")

            self.clear_fields()
            self.load_users()

        except sqlite3.IntegrityError:
            self.show_error("Username já existe!")
        except Exception as e:
            logger.error(f"Erro ao salvar usuário: {str(e)}")
            self.show_error("Erro ao salvar usuário")