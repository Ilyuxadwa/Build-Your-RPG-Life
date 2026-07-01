from unified_ui import App, Settings, tools
import flet as ft

import info
import main
import utils

def register_page_1_ui(app):
    nickname = tools.entry(app, 14, label="Nickname", hint_text="How can we call you?", on_change=lambda: check())
    nickname_message = ft.Text("", style = tools.secondary_text_style(app, 12))
    
    date_picker = ft.DatePicker(last_date = utils.get_latest(), first_date = utils.get_earliest(), on_change=lambda: check())
    date_message = ft.Text(f"Please select your birthday", style = tools.secondary_text_style(app, 12))

    next_step = ft.ElevatedButton("Continue", width = tools.adapt_dimensions(app, "w", 20), style = tools.additional_button_style(app, 14), disabled=True, on_click=lambda: next_page())

    app.add_element(app.alignment("cspace_between",
                        app.alignment("rcenter", ft.Text("Hi! To begin using this app\nwe need to meet you!", style = tools.primary_text_style(app, 24), text_align = ft.TextAlign.CENTER)),
                        app.alignment("rcenter", app.alignment("ccenter", nickname, nickname_message)),
                        app.alignment("rcenter", app.alignment("ccenter", ft.ElevatedButton("Select your birthday", style = tools.main_button_style(app, 14), on_click=lambda : app.page.show_dialog(date_picker)), date_message)),
                        app.alignment("rcenter", next_step),
                        height = tools.adapt_dimensions(app, "h", 70), width = tools.adapt_dimensions(app, "w", 100)))
    def check():
        nickname_valid = len(nickname.value) > 3 and len(nickname.value) < 20
        nickname_message.value = "" if nickname_valid else "Nickname must be between 3 and 20 characters"
        
        date_message.value = f"Your birthday is: {date_picker.value:%Y-%m-%d}" if date_picker.value else "Please select your birthday"
        if nickname_valid and date_picker.value:
            next_step.disabled = False
            next_step.style = tools.main_button_style(app, 14)
    

    def next_page():
        app.navigate("register_2")

def register_page_2_ui(app):
    height = tools.slider(app, min=100, max=200, label = "Your height (in cm)")
    next_step = ft.ElevatedButton("Continue", width = tools.adapt_dimensions(app, "w", 20), style = tools.additional_button_style(app, 14), disabled=True)
    app.add_element(app.alignment("cspace_between",
                        app.alignment("rcenter", ft.Text("Nice! Now we need to get information for\nsetting up individual goals...", style = tools.primary_text_style(app, 24), text_align = ft.TextAlign.CENTER)),
                        app.alignment("rcenter", height),
                        app.alignment("rcenter", ft.ElevatedButton("Select your birthday", style = tools.main_button_style(app, 14))),
                        app.alignment("rcenter", next_step),
                        app.alignment("rspace_between", ft.IconButton(icon = ft.Icons.ARROW_BACK, style = tools.additional_button_style(app, 10))),
                        height = tools.adapt_dimensions(app, "h", 70), width = tools.adapt_dimensions(app, "w", 100)))
    def check():
        pass
    
    def next_page():
        app.navigate("register_3")


def main_ui(app):
    categories = list(main.tasks.keys())
    rows = [categories[i : i + 2] for i in range(0, len(categories), 2)]
    buttons = []
    print(rows)
    for row in rows:
        if len(row) > 1:
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
    app.add_page("register_1", register_page_1_ui)
    app.add_page("register_2", register_page_2_ui)
    app.set_async_next(main.start)
    app.run(info.APP_NAME)