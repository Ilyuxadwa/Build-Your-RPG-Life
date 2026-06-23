from unified_ui import App, Settings, tools
import flet as ft

import info
import main
import utils

def main_ui(app):
    app.add_element(app.alignment("rcenter", 
                        ft.IconButton(ft.Icons.GET_APP_ROUNDED, width = tools.adapt_dimensions(app, "w", 6), height = tools.adapt_dimensions(app, "w", 6), style=tools.additional_button_style(app, 8, padding = 5))
                    ))
def build():
    app = App()
    app.set_size("1/2")
    app.set_version(info.VERSION)
    app.add_page("main_page", main_ui)
    #app.set_async_next(main.start)
    app.run(info.APP_NAME)