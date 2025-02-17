import flet as ft
import logging
from views.login import LoginView
from views.main_view import MainView
from database import init_db
from utils.logger import setup_logger
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    THEME_MODE,
    PRIMARY_COLOR,
    SECONDARY_COLOR
)
import os
import mimetypes
import re
import base64
import webbrowser

logger = setup_logger()

def main(page: ft.Page):
    # Configurações da janela
    page.title = WINDOW_TITLE
    page.theme_mode = THEME_MODE
    page.window_width = WINDOW_WIDTH
    page.window_height = WINDOW_HEIGHT
    page.window_resizable = False
    
    # Configurações do tema
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=getattr(ft.colors, PRIMARY_COLOR.upper()),
            secondary=getattr(ft.colors, SECONDARY_COLOR.upper()),
        ),
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )

    def route_change(event):
        """Gerencia a navegação entre as views"""
        try:
            route = event.route
            logger.info(f"Mudando rota para: {route}")

            # Limpa as views existentes
            page.views.clear()

            # Verifica se o usuário está autenticado
            #is_authenticated = hasattr(page, 'user_data') and page.user_data is not None
            is_authenticated = page.session.get("user_id") is not None  # Verifique se um user_id está na sessão, por exemplo.
            
            logger.info(f"Status de autenticação: {is_authenticated}")

            if is_authenticated:
                # Se autenticado, sempre vai para a MainView (rota '/')
                if route == "/":
                    main_view = MainView(page, serve_file_function=serve_file) # Passa a função serve_file
                    page.views.append(main_view)
                    main_view.set_current_user(page.user_data)
                    main_view.load_and_show_empenhos()  # Chame aqui, depois de adicionar à página
                    logger.info("MainView adicionada com sucesso")
                elif route == "/login":
                    # Se já estiver autenticado, redireciona para home
                    logger.info("Usuário já autenticado, redirecionando para home")
                    page.go('/')
                else:
                    page.go('/')  # Redireciona para home para qualquer outra rota
            else:
                # Se não estiver autenticado, vai para a LoginView (rota '/login')
                if route == "/login":
                    logger.info("Adicionando LoginView")
                    page.views.append(LoginView(page))
                else:
                    page.go('/login') # Redireciona para login para qualquer outra rota
            logger.info(f"Rota atual: {page.route}")
            # Atualiza a página
            page.update()

        except Exception as e:
            import traceback
            logger.error(f"Erro na navegação: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Em caso de erro, redireciona para o login
            page.views.clear()
            page.views.append(LoginView(page))
            page.go('/login')

    # Removendo on_resize
    # def on_resize(e):
    #     """Gerencia o redimensionamento da janela e atualiza a tabela"""
    #     if page.views and isinstance(page.views[-1], MainView):
    #         page.views[-1].trigger_resize()

    # Configura os gerenciadores de navegação
    page.on_route_change = route_change
    # page.on_view_pop = view_pop
    # Removendo page.on_resize
    # page.on_resize = on_resize
    
    # Inicializa o aplicativo na tela de login
    logger.info("Iniciando aplicativo")
    page.go('/login')

def serve_file(file_path):
    """Serve o arquivo estático"""
    try:
        full_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "static_files",
            file_path
        )
        if os.path.exists(full_file_path) and os.path.isfile(full_file_path):
            mime_type, _ = mimetypes.guess_type(full_file_path)
            with open(full_file_path, "rb") as f:
                 file_content = f.read()
            
            # Codifica o conteúdo do arquivo em base64
            base64_content = base64.b64encode(file_content).decode("utf-8")
            
            return f"data:{mime_type};base64,{base64_content}"
        else:
           return None
    except Exception as e:
        logger.error(f"Erro ao servir arquivo: {str(e)}")
        return None

if __name__ == '__main__':
    try:
        logger.info("Inicializando banco de dados")
        init_db()
        
        logger.info("Iniciando aplicativo Flet")
        ft.app(
            target=main,
            view=ft.WEB_BROWSER,
        )
    except Exception as e:
        logger.error(f"Erro fatal ao iniciar o aplicativo: {str(e)}")
        raise