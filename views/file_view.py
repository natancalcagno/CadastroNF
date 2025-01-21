import flet as ft
import logging
import os
from pathlib import Path
import urllib.parse
import webbrowser

logger = logging.getLogger(__name__)

class FileView(ft.UserControl):
    def __init__(self, page, serve_file_function):
        super().__init__()
        self.page = page
        self.pdf_dir = "static_files/pdf_exports"
        self.excel_dir = "static_files/exports"
        self.serve_file_function = serve_file_function
        self.init_ui()

    def build(self):
        return ft.Column(
            controls=[
                ft.Text("Gerenciamento de Arquivos", size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.files_list,
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20
        )

    def init_ui(self):
        self.files_list = ft.Column(
            controls=[
                ft.Text("Arquivos PDF", size=20, weight=ft.FontWeight.BOLD),
                self.create_file_list(self.pdf_dir, ".pdf"),
                ft.Divider(),
                ft.Text("Arquivos Excel", size=20, weight=ft.FontWeight.BOLD),
                self.create_file_list(self.excel_dir, ".xlsx"),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )

    def create_file_list(self, directory, extension):
        """Cria a lista de arquivos com base no diretório e extensão"""
        if not os.path.exists(directory):
            return ft.Text(f"Nenhum arquivo {extension} encontrado.")

        files = [f for f in os.listdir(directory) if f.endswith(extension)]

        if not files:
            return ft.Text(f"Nenhum arquivo {extension} encontrado.")

        file_controls = []
        for file in files:
            file_path = os.path.join(directory, file)
            # Converte o caminho do arquivo para URL
            file_url = self.file_path_to_url(file_path)
            file_controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(file, expand=True),
                            ft.IconButton(
                                icon=ft.icons.OPEN_IN_NEW,
                                tooltip="Abrir",
                                on_click=lambda e, path=file_url: self.open_file(path)
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda e, path=file_path, name=file: self.delete_file(path, name)
                            )
                        ],
                    ),
                    border_radius=5,
                    padding=10,
                    border=ft.border.all(1, ft.colors.OUTLINE),
                )
            )
        return ft.Column(controls=file_controls)

    def file_path_to_url(self, file_path):
        """Converte o caminho do arquivo para uma URL válida"""
        relative_path = os.path.relpath(file_path, os.path.dirname(os.path.abspath(__file__)))
        return f"/files/{relative_path}"


    def open_file(self, file_url):
      """Abre o arquivo no visualizador padrão"""
      try:
          url_content = self.serve_file_function(file_url.replace("/files/","")) # chama serve_file do main.py
          if url_content: # verifica se foi retornado um link
            webbrowser.open(url_content) # abre o link no navegador
          else:
            self.show_error("Erro ao obter o link do arquivo")
      except Exception as e:
        logger.error(f"Erro ao abrir o arquivo: {str(e)}")
        self.show_error("Erro ao abrir o arquivo")

    def delete_file(self, file_path, file_name):
        """Exclui o arquivo"""
        def confirm_delete(e):
                if e.control.data:
                    try:
                        os.remove(file_path)
                        self.show_success(f"Arquivo '{file_name}' excluído com sucesso")
                        self.files_list.controls.clear()
                        self.files_list.controls.append(ft.Text("Arquivos PDF", size=20, weight=ft.FontWeight.BOLD))
                        self.files_list.controls.append(self.create_file_list(self.pdf_dir, ".pdf"))
                        self.files_list.controls.append(ft.Divider())
                        self.files_list.controls.append(ft.Text("Arquivos Excel", size=20, weight=ft.FontWeight.BOLD))
                        self.files_list.controls.append(self.create_file_list(self.excel_dir, ".xlsx"))
                        self.files_list.update()
                    except Exception as ex:
                        logger.error(f"Erro ao excluir arquivo: {str(ex)}")
                        self.show_error("Erro ao excluir arquivo")
                dlg.open = False
                self.page.update()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar exclusão"),
            content=ft.Text(f"Tem certeza que deseja excluir o arquivo '{file_name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=confirm_delete, data=False),
                ft.TextButton("Excluir", on_click=confirm_delete, data=True),
            ],
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()


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