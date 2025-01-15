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
            is_authenticated = hasattr(page, 'user_data') and page.user_data is not None
            logger.info(f"Status de autenticação: {is_authenticated}")
            
            if route == "/" and is_authenticated:
                # Cria a MainView e configura antes de adicionar à página
                main_view = MainView(page)
                main_view.current_user = page.user_data  # Define o usuário sem chamar update()
                page.views.append(main_view)
                logger.info("MainView adicionada com sucesso")
                
            elif route == "/login":
                if is_authenticated:
                    # Se já estiver autenticado, redireciona para home sem criar nova view
                    logger.info("Usuário já autenticado, redirecionando para home")
                    page.go('/')
                    return  # Importante: retorna aqui para evitar adicionar nova view
                else:
                    # Adiciona LoginView apenas se não estiver autenticado
                    logger.info("Adicionando LoginView")
                    page.views.append(LoginView(page))
                    
            else:
                # Para qualquer outra rota, verifica autenticação
                if is_authenticated:
                    page.go('/')
                else:
                    page.go('/login')
                return  # Retorna aqui para evitar atualizações desnecessárias
                
            # Atualiza a página apenas se chegou até aqui
            page.update()
            
        except Exception as e:
            import traceback
            logger.error(f"Erro na navegação: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Em caso de erro, redireciona para o login
            page.views.clear()
            page.views.append(LoginView(page))
            page.go('/login')

    def view_pop(view):
        """Gerencia o retorno de views"""
        try:
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
        except Exception as e:
            logger.error(f"Erro ao retornar view: {str(e)}")
            page.go('/login')

    # Configura os gerenciadores de navegação
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Inicializa o aplicativo na tela de login
    logger.info("Iniciando aplicativo")
    page.go('/login')

if __name__ == '__main__':
    try:
        logger.info("Inicializando banco de dados")
        init_db()
        
        logger.info("Iniciando aplicativo Flet")
        ft.app(target=main, view=ft.WEB_BROWSER)
        
    except Exception as e:
        logger.error(f"Erro fatal ao iniciar o aplicativo: {str(e)}")
        raise

