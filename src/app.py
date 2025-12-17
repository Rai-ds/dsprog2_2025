import flet as ft
from jma_api import fetch_area_list

def main(page: ft.Page):
    page.title = "Weather Forecast App"
    page.scroll = ft.ScrollMode.AUTO

    data = fetch_area_list()
    class20s = data["class20s"]

    tiles = []
    for code, info in class20s.items():
        tiles.append(
            ft.ListTile(
                title=ft.Text(info["name"]),
                subtitle=ft.Text(f"Code: {code}")
            )
        )

    page.add(
        ft.Column(
            controls=tiles,
            expand=True
        )
    )

ft.app(target=main)
