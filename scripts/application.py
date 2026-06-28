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
    categories = list(main.tasks.keys())
    rows = [categories[i : i + 2] for i in range(0, len(categories), 2)]
    buttons = []
    print(rows)
    for row in rows:
        if len(row) > 1:
            buttons.append(app.alignment("rcenter",
                            ft.Button(row[1], style=tools.additional_button_style(app, 32, shape = ft.RoundedRectangleBorder(radius=10),
                                    side = {
                                        ft.ControlState.DEFAULT: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.HOVERED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.PRESSED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                    }), width = tools.adapt_dimensions(app, "w", 46), height = tools.adapt_dimensions(app, "w", 46)),
                            ft.Button(row[1], style=tools.additional_button_style(app, 32, shape = ft.RoundedRectangleBorder(radius=10),
                                    side = {
                                        ft.ControlState.DEFAULT: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.HOVERED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.PRESSED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                    }), width = tools.adapt_dimensions(app, "w", 46), height = tools.adapt_dimensions(app, "w", 46)),
                        expand = True, spacing = tools.adapt_dimensions(app, "w", 4)))
        else:
            buttons.append(app.alignment("rcenter",
                            ft.Button(row[0], style=tools.additional_button_style(app, 32, shape = ft.RoundedRectangleBorder(radius=10),
                                    side = {
                                        ft.ControlState.DEFAULT: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.HOVERED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                        ft.ControlState.PRESSED: ft.BorderSide(
                                            app.theme.outline_width+2, color=app.theme.outline
                                        ),
                                    }), width = tools.adapt_dimensions(app, "w", 92), height = tools.adapt_dimensions(app, "w", 46)),
                        expand = True, spacing = tools.adapt_dimensions(app, "w", 4)))
        app.add_element(app.alignment("cstart", *buttons, width = tools.adapt_dimensions(app, "w", 100), spacing = tools.adapt_dimensions(app, "w", 4), expand = True))

        
    
def build():
    app = App()
    app.set_size("1/4")
    app.set_version(info.VERSION)
    app.add_page("main_page", main_ui)
    app.add_page("register_page", register_ui)
    app.set_async_next(main.start)
    app.run(info.APP_NAME)