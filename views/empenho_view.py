import flet as ft
import logging
from database import get_db_connection
from assets.styles import get_styles
import pandas as pd
from datetime import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

logger = logging.getLogger(__name__)

class EmpenhoView(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.styles = get_styles()
        self.editing_id = None
        self.init_ui()

    def build(self):
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Gerenciamento de Empenhos", size=30, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),  # Espaçador
                        self.print_button,  # Botão de impressão
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Row([self.data_entrada, self.numero, self.empresa]),
                ft.Row([self.setor, self.numero_nota, self.data_nota]),
                ft.Row([self.valor, self.data_saida]),
                self.observacao,
                ft.Row(
                    [self.save_button, self.clear_button],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(),
                self.data_table
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )

    def init_ui(self):
        """Inicializa a interface do usuário"""
        # Título e Área de Pesquisa
        self.search_field = ft.TextField(
            label="Pesquisar",
            width=300,
            prefix_icon=ft.icons.SEARCH,
            on_change=self.filter_empenhos
        )

        self.export_button = ft.ElevatedButton(
            "Exportar para Excel",
            icon=ft.icons.DOWNLOAD,
            on_click=self.export_to_excel
        )

        # Campos do formulário
        styles = self.styles["text_field"]
        
        # Data de Entrada
        self.data_entrada = ft.TextField(
            label="Data de Entrada",
            width=styles["width"],
            value=datetime.now().strftime("%d/%m/%Y")
        )
        
        # Número do Empenho
        self.numero = ft.TextField(
            label="Número do Empenho",
            width=styles["width"],
            input_filter=ft.NumbersOnlyInputFilter()
        )
        
        # Empresa
        self.empresa = ft.TextField(
            label="Empresa",
            width=styles["width"]
        )
        
        # Setor
        self.setor = ft.Dropdown(
            label="Setor",
            width=styles["width"],
            options=[
                ft.dropdown.Option("SEMAD"),
                ft.dropdown.Option("SEMADA"),
                ft.dropdown.Option("SEMAS"),
                ft.dropdown.Option("SEMED"),
                ft.dropdown.Option("LICITAÇÃO"),
                ft.dropdown.Option("GABINETE"),
                ft.dropdown.Option("PGM"),
                ft.dropdown.Option("SEMEL"),
                ft.dropdown.Option("SEMOB"),
                ft.dropdown.Option("SEPLAGE"),
                ft.dropdown.Option("SEMMA"),
                ft.dropdown.Option("SEMUTRAN"),
                ft.dropdown.Option("SEHAB"),
                ft.dropdown.Option("SEMICS"),
                ft.dropdown.Option("SINFRAS"),
                ft.dropdown.Option("GUARDA"),
                ft.dropdown.Option("SEFIN"),
                ft.dropdown.Option("SECULT"),
                ft.dropdown.Option("SUB-APEU"),
                ft.dropdown.Option("SUB-JADER."),
            ]
        )
        
        # Número da Nota
        self.numero_nota = ft.TextField(
            label="Número da Nota",
            width=styles["width"]
        )
        
        # Data da Nota
        self.data_nota = ft.TextField(
            label="Data da Nota",
            width=styles["width"],
            hint_text="DD/MM/AAAA"
        )
        
        # Valor
        self.valor = ft.TextField(
            label="Valor",
            width=styles["width"],
            prefix_text="R$ "
        )
        
        # Data de Saída
        self.data_saida = ft.TextField(
            label="Data de Saída",
            width=styles["width"],
            disabled=True,
            value=datetime.now().strftime("%d/%m/%Y")
        )
        
        # Observação
        self.observacao = ft.TextField(
            label="Observação",
            width=styles["width"],
            multiline=True,
            min_lines=3,
            max_lines=5
        )

        # Botões
        self.save_button = ft.ElevatedButton(
            text="Salvar",
            icon=ft.icons.SAVE,
            on_click=self.add_empenho
        )

        self.clear_button = ft.ElevatedButton(
            text="Limpar",
            icon=ft.icons.CLEAR,
            on_click=lambda _: self.clear_fields()
        )

        # Adiciona botão de impressão
        self.print_button = ft.ElevatedButton(
            "Imprimir Selecionados",
            icon=ft.icons.PRINT,
            on_click=self.print_selected,
            disabled=True  # Começa desabilitado
        )

        # Lista para armazenar os empenhos selecionados
        self.selected_empenhos = []

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

        # Carrega os empenhos existentes
        self.load_empenhos()

    def load_empenhos(self, search_term=None):
        """Carrega os empenhos do banco de dados"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if search_term:
                    query = """
                        SELECT * FROM empenhos 
                        WHERE numero LIKE ? 
                        OR empresa LIKE ? 
                        OR setor LIKE ?
                        ORDER BY data_entrada DESC
                    """
                    search_pattern = f"%{search_term}%"
                    cursor.execute(query, (search_pattern, search_pattern, search_pattern))
                else:
                    cursor.execute("SELECT * FROM empenhos ORDER BY data_entrada DESC")
                
                empenhos = cursor.fetchall()

            # Limpa as linhas existentes
            self.data_table.rows.clear()

            # Adiciona os empenhos à tabela
            for empenho in empenhos:
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
                            ft.DataCell(ft.Text(empenho["data_entrada"])),
                            ft.DataCell(ft.Text(str(empenho["numero"]))),
                            ft.DataCell(ft.Text(empenho["empresa"])),
                            ft.DataCell(ft.Text(empenho["setor"])),
                            ft.DataCell(ft.Text(empenho["numero_nota"])),
                            ft.DataCell(ft.Text(empenho["data_nota"])),
                            ft.DataCell(ft.Text(f"R$ {empenho['valor']:.2f}")),
                            ft.DataCell(ft.Text(empenho["data_saida"])),
                            ft.DataCell(ft.Text(empenho["observacao"])),
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

            self.update()

        except Exception as e:
            logger.error(f"Erro ao carregar empenhos: {str(e)}")
            self.show_error("Erro ao carregar empenhos")

    def filter_empenhos(self, e):
        """Filtra os empenhos com base no texto de pesquisa"""
        self.load_empenhos(e.control.value)

    def edit_empenho(self, e):
        """Carrega os dados do empenho para edição"""
        try:
            empenho_id = e.control.data
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM empenhos WHERE id = ?", (empenho_id,))
                empenho = cursor.fetchone()

            if empenho:
                self.editing_id = empenho_id
                self.data_entrada.value = empenho["data_entrada"]
                self.numero.value = str(empenho["numero"])
                self.empresa.value = empenho["empresa"]
                self.setor.value = empenho["setor"]
                self.numero_nota.value = empenho["numero_nota"]
                self.data_nota.value = empenho["data_nota"]
                self.valor.value = str(empenho["valor"])
                self.data_saida.value = empenho["data_saida"]
                self.observacao.value = empenho["observacao"]
                self.save_button.text = "Atualizar"
                self.update()

        except Exception as e:
            logger.error(f"Erro ao carregar empenho para edição: {str(e)}")
            self.show_error("Erro ao carregar empenho para edição")

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
                        numero, empresa, setor,
                        numero_nota, data_nota, valor, data_saida,
                        created_at
                    FROM empenhos 
                    ORDER BY data_entrada DESC
                """, conn)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"empenhos_{timestamp}.xlsx"
            
            export_dir = "exports"
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            
            filepath = os.path.join(export_dir, filename)
            df.to_excel(filepath, index=False, sheet_name="Empenhos")
            
            self.show_success(f"Dados exportados com sucesso para {filename}")

        except Exception as e:
            logger.error(f"Erro ao exportar dados: {str(e)}")
            self.show_error("Erro ao exportar dados")

    def validate_inputs(self) -> bool:
        """Valida os campos de entrada"""
        try:
            # Validação da Data de Entrada
            if not self.data_entrada.value:
                self.show_error("Data de entrada é obrigatória")
                return False
            
            # Validação do Número do Empenho
            if not self.numero.value:
                self.show_error("Número do empenho é obrigatório")
                return False
            try:
                int(self.numero.value)
            except ValueError:
                self.show_error("Número do empenho deve conter apenas números")
                return False
            
            # Validação da Empresa
            if not self.empresa.value:
                self.show_error("Empresa é obrigatória")
                return False
            
            # Validação do Setor
            if not self.setor.value:
                self.show_error("Setor é obrigatório")
                return False
            
            # Validação do Número da Nota
            if not self.numero_nota.value:
                self.show_error("Número da nota é obrigatório")
                return False
            
            # Validação da Data da Nota
            if not self.data_nota.value:
                self.show_error("Data da nota é obrigatória")
                return False
            
            # Validação do Valor
            if not self.valor.value:
                self.show_error("Valor é obrigatório")
                return False
            
            # Remove formatação do valor e converte para float
            valor_str = self.valor.value.replace('R$ ', '').replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                if valor <= 0:
                    self.show_error("Valor deve ser maior que zero")
                    return False
            except ValueError:
                self.show_error("Valor inválido")
                return False
            
            return True

        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            self.show_error("Erro ao validar os dados")
            return False

    def validate_date(self, date_str: str) -> bool:
        """Valida o formato da data"""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def clear_fields(self):
        """Limpa os campos do formulário"""
        self.editing_id = None
        self.data_entrada.value = datetime.now().strftime("%d/%m/%Y")
        self.numero.value = ""
        self.empresa.value = ""
        self.setor.value = None
        self.numero_nota.value = ""
        self.data_nota.value = ""
        self.valor.value = ""
        self.data_saida.value = datetime.now().strftime("%d/%m/%Y")
        self.observacao.value = ""
        self.save_button.text = "Salvar"
        self.update()

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

    def add_empenho(self, e):
        """Adiciona ou atualiza um empenho"""
        try:
            if not self.validate_inputs():
                return

            # Prepara os dados do empenho
            empenho_data = {
                "data_entrada": self.data_entrada.value,
                "numero": int(self.numero.value),
                "empresa": self.empresa.value,
                "setor": self.setor.value,
                "numero_nota": self.numero_nota.value,
                "data_nota": self.data_nota.value,
                "valor": float(self.valor.value.replace('R$ ', '').replace('.', '').replace(',', '.')),
                "data_saida": self.data_saida.value,
                "observacao": self.observacao.value
            }

            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                if self.editing_id:
                    # Atualiza empenho existente
                    cursor.execute("""
                        UPDATE empenhos 
                        SET data_entrada = ?, 
                            numero = ?, 
                            empresa = ?, 
                            setor = ?, 
                            numero_nota = ?, 
                            data_nota = ?,
                            valor = ?, 
                            data_saida = ?, 
                            observacao = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        empenho_data["data_entrada"],
                        empenho_data["numero"],
                        empenho_data["empresa"],
                        empenho_data["setor"],
                        empenho_data["numero_nota"],
                        empenho_data["data_nota"],
                        empenho_data["valor"],
                        empenho_data["data_saida"],
                        empenho_data["observacao"],
                        self.editing_id
                    ))
                    self.show_success("Empenho atualizado com sucesso!")
                else:
                    # Insere novo empenho
                    cursor.execute("""
                        INSERT INTO empenhos (
                            data_entrada, 
                            numero, 
                            empresa, 
                            setor,
                            numero_nota, 
                            data_nota, 
                            valor,
                            data_saida, 
                            observacao
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        empenho_data["data_entrada"],
                        empenho_data["numero"],
                        empenho_data["empresa"],
                        empenho_data["setor"],
                        empenho_data["numero_nota"],
                        empenho_data["data_nota"],
                        empenho_data["valor"],
                        empenho_data["data_saida"],
                        empenho_data["observacao"]
                    ))
                    self.show_success("Empenho cadastrado com sucesso!")

            # Limpa os campos e recarrega a lista
            self.clear_fields()
            self.load_empenhos()

        except ValueError as ve:
            logger.error(f"Erro de validação: {str(ve)}")
            self.show_error("Por favor, verifique os valores informados")
        except Exception as e:
            logger.error(f"Erro ao salvar empenho: {str(e)}")
            self.show_error("Erro ao salvar empenho")

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
            filename = f"empenhos_impressao_{timestamp}.pdf"
            
            # Cria o diretório se não existir
            pdf_dir = "pdf_exports"
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

            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()

            # Cabeçalho do documento
            elements.append(Paragraph("PROTOCOLO PARA ENTREGA DE NOTAS FISCAIS \n UNIDADE DE CONTROLE INTERNO", styles['Title']))
            elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
            elements.append(Paragraph("<br/><br/>", styles['Normal']))

            # Dados da tabela
            data = [["Data Entrada", "Número", "Empresa", "Setor", "Nº Nota", "Valor"]]
            for empenho in empenhos:
                data.append([
                    empenho["data_entrada"],
                    str(empenho["numero"]),
                    empenho["empresa"],
                    empenho["setor"],
                    empenho["numero_nota"],
                    f"R$ {empenho['valor']:.2f}"
                ])

            # Cria a tabela
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)
            doc.build(elements)

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            raise
