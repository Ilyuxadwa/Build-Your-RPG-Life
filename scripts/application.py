from unified_ui import App, Settings, tools
import flet as ft

import info
import main
import utils

def register_ui(app):
    app.add_element(app.alignment("rcenter", 
                        ft.Container(bgcolor=app.theme.secondary, width=tools.adapt_dimensions(app, "w", 80), height=tools.adapt_dimensions(app, "h", 20))
                    ))
    app.add_element(app.alignment("rcenter", 
                        ft.Container(bgcolor=app.theme.secondary, width=tools.adapt_dimensions(app, "w", 80), height=tools.adapt_dimensions(app, "h", 20))
                    ))

def main_ui(app):
    app.add_element(app.alignment("rcenter", 
                        ft.Container(bgcolor=app.theme.secondary, width=tools.adapt_dimensions(app, "w", 80), height=tools.adapt_dimensions(app, "h", 20))
                    ))
    app.add_element(app.alignment("rcenter", 
                        ft.Container(bgcolor=app.theme.secondary, width=tools.adapt_dimensions(app, "w", 80), height=tools.adapt_dimensions(app, "h", 20))
                    ))
def build():
    app = App()
    app.set_size("1/4")
    app.set_version(info.VERSION)
    app.add_page("main_page", main_ui)
    app.add_page("register_page", register_ui)
    app.set_async_next(main.start)
    app.run(info.APP_NAME)