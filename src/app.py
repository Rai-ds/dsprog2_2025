import flet as ft

def main(page: ft.Page):
    page.title = "Weather App Test"
    page.add(ft.Text("Flet is working"))

ft.app(target=main)
