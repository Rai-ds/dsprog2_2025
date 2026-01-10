import flet as ft
import jma_api
import db  

def main(page: ft.Page):
    page.title = "天気予報アプリ (DB 追加)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1000
    page.window_height = 700
    page.padding = 0

    db.init_db()

    area_data = jma_api.get_area_data()

    def create_card(forecast):
        min_c = "blue200" if forecast["min"] != "-" else "grey"
        max_c = "red200" if forecast["max"] != "-" else "grey"
        
        return ft.Container(
            width=180, height=220,
            bgcolor="#2b3035",
            border_radius=15,
            padding=20,
            content=ft.Column(
                [
                    ft.Text(forecast["date"], weight="bold", size=16),
                    ft.Container(height=10),
                    ft.Image(src=forecast["icon"], width=70, height=70),
                    ft.Container(height=10),
                    ft.Text(forecast["weather"], size=12, text_align="center", no_wrap=False),
                    ft.Container(expand=True),
                    ft.Row(
                        [
                            ft.Text(f"{forecast['min']}°C", color=min_c, size=16),
                            ft.Text("/", color="grey", size=16),
                            ft.Text(f"{forecast['max']}°C", color=max_c, size=16),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                horizontal_alignment="center",
                spacing=0
            )
        )

    weather_grid = ft.Row(wrap=True, scroll="auto", spacing=20)
    header = ft.Text("地域を選択してください", size=28, weight="bold")
    
    main_area = ft.Container(
        expand=True,
        padding=40,
        content=ft.Column(
            [
                header,
                ft.Divider(height=30, color="grey800"),
                weather_grid
            ]
        )
    )

    def on_click(e):
        name = e.control.title.value
        code = e.control.data
        
        header.value = f"{name} の天気予報"
        weather_grid.controls.clear()
        weather_grid.controls.append(ft.ProgressRing())
        page.update()
        
        api_data = jma_api.fetch_weather_data(code)
        
        if api_data:
            db.save_forecasts(code, api_data)
        
        db_data = db.get_forecasts(code)
        
        weather_grid.controls.clear()
        if db_data:
            for item in db_data:
                weather_grid.controls.append(create_card(item))
        else:
            weather_grid.controls.append(ft.Text("データ取得エラー (またはDBエラー)"))
        
        page.update()

    sidebar_items = []
    sidebar_items.append(ft.Container(padding=15, content=ft.Text("地域を選択", size=14, weight="bold", color="grey")))

    for region, prefs in area_data.items():
        tiles = []
        for p_name, p_code in prefs.items():
            tiles.append(
                ft.ListTile(
                    title=ft.Text(p_name, size=14),
                    data=p_code,
                    on_click=on_click
                )
            )
        
        sidebar_items.append(
            ft.ExpansionTile(
                title=ft.Text(region),
                controls=tiles,
                text_color="white",
                collapsed_text_color="white70"
            )
        )

    sidebar = ft.Container(
        width=250,
        bgcolor="#1f2329",
        content=ft.ListView(controls=sidebar_items, padding=10),
        border=ft.border.only(right=ft.BorderSide(1, "grey900"))
    )

    page.add(
        ft.Row([sidebar, main_area], spacing=0, expand=True)
    )

if __name__ == "__main__":
    ft.app(target=main)