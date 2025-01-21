import flet as ft
import logging
from views.user_view import UserView
from views.empenho_view import EmpenhoView
from views.file_view import FileView  # Importe a FileView
from database import get_db_connection
from assets.styles import get_styles
import traceback
import pandas as pd
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class MainView(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.styles = get_styles()
        self.route = "/"
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        """Inicializa a interface do usuário"""
        try:
            # Menu de navegação superior
            self.menu = ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text="Início",
                        icon=ft.icons.HOME,
                        on_click=lambda e: self.menu_change(0),
                    ),
                    ft.ElevatedButton(
                        text="Usuários",
                        icon=ft.icons.PERSON,
                        on_click=lambda e: self.menu_change(1),
                    ),
                    ft.ElevatedButton(
                        text="Empenhos",
                        icon=ft.icons.ATTACH_MONEY,
                        on_click=lambda e: self.menu_change(2),
                    ),
                     ft.ElevatedButton(
                        text="Arquivos",
                        icon=ft.icons.FOLDER_OPEN,
                        on_click=lambda e: self.menu_change(3),
                    ),
                    ft.ElevatedButton(
                        text="Sair",
                        icon=ft.icons.LOGOUT,
                        on_click=self.logout,
                        bgcolor=ft.colors.RED_400,
                        color=ft.colors.WHITE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
            )

            # Cabeçalho com título e menu
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(
                            "Sistema de Empenhos",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE
                        ),
                        ft.Container(expand=True),  # Espaçador flexível
                        self.menu,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.padding.only(left=20, right=20, top=10, bottom=10),
                bgcolor=ft.colors.SURFACE_VARIANT,
            )
            
            # Lista para armazenar os empenhos selecionados
            self.selected_empenhos = []

            # Botões de ação
            self.print_button = ft.ElevatedButton(
                "Imprimir Selecionados",
                icon=ft.icons.PRINT,
                on_click=self.print_selected,
                disabled=True
            )

            self.export_button = ft.ElevatedButton(
                "Exportar para Excel",
                icon=ft.icons.DOWNLOAD,
                on_click=self.export_to_excel
            )

            # Área de pesquisa
            self.search_field = ft.TextField(
                label="Pesquisar empenhos",
                width=400,
                prefix_icon=ft.icons.SEARCH,
                on_change=self.filter_empenhos
            )
            
            # Tabela de empenhos
            self.data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Selecionar")),
                    ft.DataColumn(ft.Text("Data Entrada")),
                    ft.DataColumn(ft.Text("Número")),
                    ft.DataColumn(ft.Text("Empresa")),
                    ft.DataColumn(ft.Text("Setor")),
                    ft.DataColumn(ft.Text("Nº Nota")),
                    ft.DataColumn(ft.Text("Data Nota")),
                    ft.DataColumn(ft.Text("Valor")),
                    ft.DataColumn(ft.Text("Data Saída")),
                    ft.DataColumn(ft.Text("Observação")),
                    ft.DataColumn(ft.Text("Ações")),
                ],
                rows=[]
            )

            # Área de conteúdo - Layout da Home
            self.content_area = ft.Column(
                controls=[
                    # Cabeçalho com boas-vindas e botões de ação
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Bem-vindo, {self.current_user['username'] if self.current_user else ''}!",
                                size=24,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(expand=True),  # Espaçador
                            self.print_button,
                            self.export_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),

                    # Área de pesquisa
                    ft.Container(
                        content=self.search_field,
                        padding=ft.padding.only(bottom=20)
                    ),

                    # Tabela de empenhos
                    ft.Text(
                        "Empenhos Cadastrados:",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),
                    
                    self.data_table
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO
            )

            # Container principal
            self.main_container = ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        ft.Container(
                            content=self.content_area,
                            expand=True,
                            padding=20
                        )
                    ],
                    expand=True,
                    spacing=0,
                ),
                expand=True
            )

            # Define os controles da view
            self.controls = [self.main_container]

        except Exception as e:
            logger.error(f"Erro ao inicializar interface: {str(e)}")
            self.controls = [ft.Text("Erro ao carregar interface")]

    def build(self):
        """Retorna o container principal"""
        return self.main_container

    def menu_change(self, index):
        """Gerencia a mudança de menu"""
        try:
            logger.info(f"Mudando para o menu índice: {index}")

            # Verifica permissão para acessar a tela de usuários
            if index == 1:  # Usuários
                if not self.current_user or self.current_user.get("user_type") != "admin":
                    logger.warning("Tentativa de acesso não autorizado à área de usuários")
                    self.show_error("Acesso não autorizado")
                    return
                logger.info("Acesso autorizado para área de usuários")

            # Atualiza a área de conteúdo com base na seleção do menu
            if index == 0:  # Home
                logger.info("Carregando view Home")
                self.content_area.controls = [
                    # Cabeçalho com boas-vindas e botões de ação
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"Bem-vindo, {self.current_user['username'] if self.current_user else ''}!",
                                size=24,
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Container(expand=True),  # Espaçador
                            self.print_button,
                            self.export_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),

                    # Área de pesquisa
                    ft.Container(
                        content=self.search_field,
                        padding=ft.padding.only(bottom=20)
                    ),

                    # Tabela de empenhos
                    ft.Text(
                        "Empenhos Cadastrados:",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    self.data_table
                ]
                
                # Carrega e exibe os dados dos empenhos
                self.load_and_show_empenhos()

            elif index == 1:  # Usuários
                logger.info("Carregando view Usuários")
                self.content_area.controls = [UserView(self.page)]

            elif index == 2:  # Empenhos
                logger.info("Carregando view Empenhos")
                self.content_area.controls = [EmpenhoView(self.page)]
            
            elif index == 3: # Arquivos
                logger.info("Carregando view Arquivos")
                self.content_area.controls = [FileView(self.page)]

            # Atualiza a área de conteúdo
            self.content_area.update()

        except Exception as e:
            logger.error(f"Erro ao mudar menu: {str(e)}")
            self.show_error(f"Erro ao mudar menu: {e}")

    def load_and_show_empenhos(self):
        """Carrega os empenhos e atualiza a tabela"""
        self.load_empenhos()
        if self.data_table.page:  # Verifica se a data_table está na página
            self.data_table.update()



    def get_empenhos(self, search_term=None):
        """Busca os empenhos mais recentes"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if search_term:
                    # Busca com filtro
                    cursor.execute("""
                        SELECT id, data_entrada, numero, empresa, setor, 
                               numero_nota, data_nota, valor, data_saida, 
                               observacao, created_at 
                        FROM empenhos 
                        WHERE LOWER(numero) LIKE ? 
                        OR LOWER(empresa) LIKE ? 
                        OR LOWER(setor) LIKE ?
                        ORDER BY data_entrada DESC
                    """, (
                        f"%{search_term.lower()}%",
                        f"%{search_term.lower()}%",
                        f"%{search_term.lower()}%"
                    ))
                else:
                    # Busca todos
                    cursor.execute("""
                        SELECT id, data_entrada, numero, empresa, setor, 
                               numero_nota, data_nota, valor, data_saida, 
                               observacao, created_at 
                        FROM empenhos 
                        ORDER BY data_entrada DESC
                    """)
                    
                return [
                    {
                        "id": row[0],
                        "data_entrada": row[1],
                        "numero": row[2],
                        "empresa": row[3],
                        "setor": row[4],
                        "numero_nota": row[5],
                        "data_nota": row[6],
                        "valor": row[7],
                        "data_saida": row[8],
                        "observacao": row[9],
                        "created_at": row[10]
                    } for row in cursor.fetchall()
                ]
        except Exception as e:
            logger.error(f"Erro ao buscar empenhos: {str(e)}")
            return []

    def on_select_empenho(self, e):
        """Gerencia a seleção de empenhos"""
        try:
            empenho_id = e.control.data
            if e.control.value:  # Se foi selecionado
                self.selected_empenhos.append(empenho_id)
            else:  # Se foi desselecionado
                self.selected_empenhos.remove(empenho_id)
            
            # Habilita/desabilita botão de impressão
            self.print_button.disabled = len(self.selected_empenhos) == 0
            self.print_button.update()

        except Exception as e:
            logger.error(f"Erro ao selecionar empenho: {str(e)}")
            self.show_error("Erro ao selecionar empenho")

    def print_selected(self, e):
        """Gera PDF com os empenhos selecionados"""
        try:
            if not self.selected_empenhos:
                self.show_error("Nenhum empenho selecionado")
                return

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Busca os dados dos empenhos selecionados
                placeholders = ','.join('?' * len(self.selected_empenhos))
                cursor.execute(f"""
                    SELECT * FROM empenhos 
                    WHERE id IN ({placeholders})
                    ORDER BY data_entrada DESC
                """, self.selected_empenhos)
                
                empenhos = cursor.fetchall()

            # Gera o PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"empenhos_PDF_{timestamp}.pdf"
            
            # Cria o diretório se não existir
            pdf_dir = "static_files/pdf_exports"
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir)
            
            filepath = os.path.join(pdf_dir, filename)
            
            # Gera o PDF usando reportlab
            self.generate_pdf(empenhos, filepath)
            
            self.show_success(f"PDF gerado com sucesso: {filename}")

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            self.show_error("Erro ao gerar PDF")

    def generate_pdf(self, empenhos, filepath):
        """Gera o PDF com os dados dos empenhos"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch

            # Criar documento em modo paisagem para melhor visualização
            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()

            # Estilo personalizado para o título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=1,
                alignment=1  # Centralizado
            )

            # Cabeçalho do documento
            elements.append(Paragraph("PROTOCOLO PARA ENTREGA DE NOTAS FISCAIS", styles['Title']))
            elements.append(Paragraph(" UNIDADE DE CONTROLE INTERNO", title_style))
            elements.append(Paragraph("Atestamos que as respectivas notas fiscais foram entregues para a Secretaria de Finanças na presente data.", styles['Normal']))
            elements.append(Spacer(1, 20))

            # Cabeçalhos da tabela
            headers = [
                "Nº Empenho",
                "Empresa",
                "Setor",
                "Nº Nota",
                "Data Nota",
                "Valor"
            ]

            # Dados da tabela
            data = [headers]  # Primeira linha são os cabeçalhos
            
            # Adiciona os dados de cada empenho
            for empenho in empenhos:
                data.append([
                    str(empenho["numero"]),
                    empenho["empresa"],
                    empenho["setor"],
                    empenho["numero_nota"],
                    empenho["data_nota"],
                    f"R$ {empenho['valor']:.2f}"
                ])

            # Configurações da tabela
            col_widths = [1.2*inch, 2.5*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch]  # Larguras personalizadas
            table = Table(data, colWidths=col_widths)
            
            # Estilo da tabela
            table.setStyle(TableStyle([
                # Estilo do cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Estilo do conteúdo
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # Centraliza todo o conteúdo
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Espaçamento interno das células
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))

            elements.append(table)
            
            # Adiciona rodapé com data e hora
            elements.append(Spacer(1, 20))
            footer_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            elements.append(Paragraph(footer_text, styles['Normal']))

            # Gera o PDF
            doc.build(elements)

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            raise

    def load_empenhos(self, search_term=None):
        """Carrega os empenhos do banco de dados"""
        try:
            # Limpa as linhas existentes
            self.data_table.rows.clear()

            # Busca os empenhos do banco de dados
            empenhos = self.get_empenhos(search_term)

            if not empenhos:
                # Adiciona uma linha indicando que não há empenhos
                self.data_table.rows.append(
                    ft.DataRow(
                        cells=[ft.DataCell(ft.Text("Nenhum empenho encontrado")) for _ in range(len(self.data_table.columns))] # Cria celulas vazias para todas as colunas
                    )
                )
            else:
                # Adiciona os empenhos à tabela
                for empenho in empenhos:
                    # Limita o tamanho da observação para não quebrar o layout
                    observacao = empenho["observacao"] or ""
                    if len(observacao) > 30:
                        observacao = observacao[:27] + "..."

                    self.data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Checkbox(
                                        value=False,
                                        data=empenho["id"],
                                        on_change=self.on_select_empenho
                                    )
                                ),
                                ft.DataCell(ft.Text(empenho["data_entrada"] if empenho["data_entrada"] else "")), # Trata como string
                                ft.DataCell(ft.Text(str(empenho["numero"]))),
                                ft.DataCell(ft.Text(empenho["empresa"])),
                                ft.DataCell(ft.Text(empenho["setor"])),
                                ft.DataCell(ft.Text(empenho["numero_nota"])),
                                ft.DataCell(ft.Text(empenho["data_nota"] if empenho["data_nota"] else "")), # Trata como string
                                ft.DataCell(ft.Text(f"R$ {empenho['valor']:.2f}")),
                                ft.DataCell(ft.Text(empenho["data_saida"] if empenho["data_saida"] else "")), # Trata como string
                                ft.DataCell(
                                    ft.Container(
                                        content=ft.Text(
                                            observacao,
                                            tooltip=empenho["observacao"] if empenho["observacao"] else ""
                                        )
                                    )
                                ),
                                ft.DataCell(
                                    ft.Row(
                                        [
                                            ft.IconButton(
                                                icon=ft.icons.EDIT,
                                                icon_color=ft.colors.BLUE,
                                                tooltip="Editar",
                                                data=empenho["id"],
                                                on_click=self.edit_empenho
                                            ),
                                            ft.IconButton(
                                                icon=ft.icons.DELETE,
                                                icon_color=ft.colors.RED,
                                                tooltip="Excluir",
                                                data=empenho["id"],
                                                on_click=self.delete_empenho
                                            ),
                                        ]
                                    )
                                ),
                            ]
                        )
                    )

        except Exception as e:
            logger.error(f"Erro ao carregar empenhos: {str(e)}")
            self.show_error("Erro ao carregar empenhos")

    def filter_empenhos(self, e):
        """Filtra os empenhos com base no texto de pesquisa"""
        self.load_empenhos(e.control.value)
        self.data_table.update()


    def edit_empenho(self, e):
        """Redireciona para a tela de edição do empenho"""
        try:
            empenho_id = e.control.data
            self.page.go(f"/empenho?id={empenho_id}")
        except Exception as e:
            logger.error(f"Erro ao redirecionar para edição: {str(e)}")
            self.show_error("Erro ao abrir empenho para edição")

    def delete_empenho(self, e):
        """Exclui um empenho"""
        try:
            empenho_id = e.control.data
            
            def confirm_delete(e):
                if e.control.data:
                    try:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM empenhos WHERE id = ?", (empenho_id,))
                        self.show_success("Empenho excluído com sucesso!")
                        self.load_empenhos()
                    except Exception as ex:
                        logger.error(f"Erro ao excluir empenho: {str(ex)}")
                        self.show_error("Erro ao excluir empenho")
                dlg.open = False
                self.page.update()

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar exclusão"),
                content=ft.Text("Tem certeza que deseja excluir este empenho?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=confirm_delete, data=False),
                    ft.TextButton("Excluir", on_click=confirm_delete, data=True),
                ],
            )
            
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()

        except Exception as e:
            logger.error(f"Erro ao excluir empenho: {str(e)}")
            self.show_error("Erro ao excluir empenho")

    def export_to_excel(self, e):
        """Exporta os empenhos para um arquivo Excel"""
        try:
            with get_db_connection() as conn:
                df = pd.read_sql_query("""
                    SELECT 
                        data_entrada, numero, empresa, setor,
                        numero_nota, data_nota, valor, data_saida,
                        observacao, created_at
                    FROM empenhos 
                    ORDER BY data_entrada DESC
                """, conn)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"empenhos_{timestamp}.xlsx"
            
            export_dir = "static_files/exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            filepath = os.path.join(export_dir, filename)
            df.to_excel(filepath, index=False, sheet_name="Empenhos")
            
            self.show_success(f"Dados exportados com sucesso para {filename}")

        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}")
            self.show_error("Erro ao exportar dados")

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

    def set_current_user(self, user_data):
        """Define o usuário atual"""
        self.current_user = user_data
        self.content_area.controls = [
            # Cabeçalho com boas-vindas e botões de ação
            ft.Row(
                controls=[
                    ft.Text(
                        f"Bem-vindo, {self.current_user['username'] if self.current_user else ''}!",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(expand=True),  # Espaçador
                    self.print_button,
                    self.export_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),

            # Área de pesquisa
            ft.Container(
                content=self.search_field,
                padding=ft.padding.only(bottom=20)
            ),

            # Tabela de empenhos
            ft.Text(
                "Empenhos Cadastrados:",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            self.data_table
        ]
        self.load_and_show_empenhos()
        # Remova esta linha:
        # self.update()

    # def update_menu_permissions(self):
    #     """Atualiza as permissões do menu baseado no tipo de usuário"""
    #     if self.current_user and self.current_user.get("user_type") != "admin":
    #         self.rail.destinations[2].disabled = True
    #     else:
    #         self.rail.destinations[2].disabled = False

    def logout(self, e):
        """Realiza o logout do usuário"""
        try:
            logger.info("Iniciando logout...")
            # Limpa os dados da sessão
            self.page.session.clear()
            self.current_user = None
            logger.info("Sessão limpa.")

            # Limpa a pilha de visualizações
            self.page.views.clear()
            logger.info("Pilha de visualizações limpa.")
            
            # Forçar atualização da página
           
            logger.info("Página atualizada (antes do redirecionamento).")

            # Redireciona para a tela de login
            self.page.go("/login")
            logger.info("Redirecionando para /login...")
            
            print(f"DEBUG: self.page no logout: {self.page}")  # Adicione esta linha
            

        except Exception as e:
            logger.error(f"Erro ao fazer logout: {str(e)}")
            self.show_error("Erro ao fazer logout")