import flet as ft

def get_styles():
    return {
        "text_field": {
            "width": 400,
            "border_color": ft.colors.BLUE,
            "focused_border_color": ft.colors.BLUE_700,
            "text_size": 16,
        },
        "button": {
            "width": 150,
            "bgcolor": ft.colors.BLUE,
            "color": ft.colors.WHITE,
            "style": ft.ButtonStyle(
                padding=ft.padding.all(15),
                shape={
                    "": ft.RoundedRectangleBorder(radius=8),
                },
            ),
        }
    }