import flet as ft
import logging
from database import validate_login
from assets.styles import get_styles
from views.main_view import MainView

logger = logging.getLogger(__name__)

class LoginView(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.styles = get_styles()
        self.route = "/login"  # Define a rota da view
        self.init_components()
        self.build()
        self.controls = [self.main_container]  # Define os controles da view

    def init_components(self):
        """Inicializa os componentes da interface"""
        # Campo de usuário
        self.username = ft.TextField(
            label="Usuário",
            width=400,
            border_color=ft.colors.BLUE,
            autofocus=True,
            on_submit=self.login
        )

        # Campo de senha
        self.password = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True,
            width=400,
            border_color=ft.colors.BLUE,
            on_submit=self.login
        )

        # Botão de login
        self.login_button = ft.ElevatedButton(
            "Entrar",
            width=150,
            on_click=self.login,
            icon=ft.icons.LOGIN
        )

        # Campo de mensagem
        self.message = ft.Text(
            color=ft.colors.RED,
            size=14,
            weight=ft.FontWeight.BOLD
        )

        # Indicador de carregamento
        self.progress_ring = ft.ProgressRing(visible=False)

        # Container principal
        self.main_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Sistema de Empenhos",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.BLUE
                    ),
                    ft.Container(height=20),  # Espaçamento
                    self.username,
                    self.password,
                    ft.Row(
                        [self.login_button, self.progress_ring],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    self.message,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.padding.all(20),
        )

    def login(self, e):
        """Processa o login do usuário"""
        try:
            if not self.validate_inputs():
                return

            # Mostra indicador de carregamento
            self.progress_ring.visible = True
            self.login_button.disabled = True
            self.update()

            # Valida credenciais
            user_data = validate_login(self.username.value, self.password.value)
            if user_data:
                self.show_success("Login realizado com sucesso!")
                
                # Armazena os dados do usuário na página
                self.page.user_data = user_data
                
                # Apenas navega para a rota principal
                # O sistema de rotas cuidará de criar e adicionar a MainView
                self.page.go('/')
            else:
                self.show_error("Usuário ou senha incorretos")
                self.password.value = ""
                self.password.focus()
        
        except Exception as ex:
            logger.error(f"Erro no login: {str(ex)}")
            self.show_error("Erro ao realizar login. Tente novamente.")
        
        finally:
            # Esconde indicador de carregamento
            self.progress_ring.visible = False
            self.login_button.disabled = False
            self.update()

    def validate_inputs(self) -> bool:
        """Valida os campos de entrada"""
        if not self.username.value or not self.username.value.strip():
            self.show_error("Por favor, insira o nome de usuário")
            self.username.focus()
            return False
        
        if not self.password.value or not self.password.value.strip():
            self.show_error("Por favor, insira a senha")
            self.password.focus()
            return False
            
        return True

    def show_error(self, message: str):
        """Exibe mensagem de erro"""
        self.message.value = message
        self.message.color = ft.colors.RED
        self.update()

    def show_success(self, message: str):
        """Exibe mensagem de sucesso"""
        self.message.value = message
        self.message.color = ft.colors.GREEN
        self.update()
