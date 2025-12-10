import flet as ft


def main(page: ft.Page):
    #text to show counter

    counter = ft.Text("0", size=50, data=0)
    
    # here

    
    
    # to call the funciton when the button is pressed
    def increment_click(e):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()
    
    def decrement_click(e):
        counter.data -= 1
        counter.value = str(counter.data)
        counter.update()
    # button to increase the counter
    page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=increment_click)
    
    # safe arera to show the counter in the cneter of the page
    page.add(
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.alignment.center,
            ),
            expand=True,
        ),
        ft.FloatingActionButton(icon=ft.Icons.REMOVE, on_click=decrement_click),
    )


ft.app(main)