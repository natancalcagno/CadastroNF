import flet as ft
import os
import logging
import webbrowser  # Importa o módulo webbrowser para abrir arquivos

logger = logging.getLogger(__name__)

class FileView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.list_view = ft.ListView()  # Criação do ListView
        self.controls = [self.list_view]  # Adiciona o ListView aos controles da página
        self.load_files()  # Carrega os arquivos

    def load_files(self):
        """Carrega os arquivos PDF e XLSX do diretório e os adiciona ao ListView"""
        try:
            directory = "static_exports"  # Diretório onde os arquivos estão armazenados

            if not os.path.exists(directory):
                logger.error(f"Diretório não encontrado: {directory}")
                self.show_error("Diretório não encontrado.")
                return

            self.list_view.controls.clear()  # Limpa o ListView antes de adicionar novos itens

            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and (filename.endswith('.pdf') or filename.endswith('.xlsx')):
                    # Adiciona o arquivo ao ListView com a opção de abrir
                    self.list_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(filename),
                            on_click=lambda e, path=file_path: self.open_file(path)  # Passa o caminho do arquivo
                        )
                    )

            self.list_view.update()  # Atualiza o ListView

        except Exception as e:
            logger.error(f"Erro ao carregar arquivos: {str(e)}")
            self.show_error("Erro ao carregar arquivos.")

    def open_file(self, file_path):
        """Abre o arquivo selecionado"""
        try:
            logger.info(f"Abrindo arquivo: {file_path}")
            webbrowser.open(file_path)  # Abre o arquivo no visualizador padrão
        except Exception as e:
            logger.error(f"Erro ao abrir arquivo: {str(e)}")
            self.show_error("Erro ao abrir arquivo.")

    def show_error(self, message: str):
        """Exibe uma mensagem de erro"""
        self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                bgcolor=ft.colors.RED_400,
                duration=3000
            )
        )