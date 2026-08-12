import asyncio

from unified_ui import App, Settings, tools
import flet as ft

import info
import main
from goals import ActionGoal, AmountGoal, TimeGoal, DailyGoal, WeeklyGoal, CustomGoal, InputMode, GoalStatus
import utils
import register_manager
from tasks import Task, ActionTask, AmountTask, TimeTask
from achievements import Achievement

from datetime import datetime, timedelta, date, time
import copy

def achievements_dialog(app):
    def reached_card(achievement: Achievement):
        return ft.Container(content = app.alignment("cstart", 
                                ft.Text(achievement.message, style = tools.primary_text_style(app, 24)),
                                ft.Text(achievement.task.replace("{number}", str(achievement.number)), style = tools.primary_text_style(app, 18)),
                            ), bgcolor = app.theme.entry, border_radius = 10, padding = 10, width = tools.adapt_dimensions(app, "w", 50))

    def unreached_card(achievement: Achievement):
            return ft.Container(content = app.alignment("cstart", 
                                    ft.Text(achievement.message, style = tools.secondary_text_style(app, 24)),
                                    ft.Text(achievement.task.replace("{number}", str(achievement.number)), style = tools.secondary_text_style(app, 18)),
                                ), bgcolor = app.theme.additional_color, border_radius = 10, padding = 10, width = tools.adapt_dimensions(app, "w", 50))

    achievements = main.achievements
    gained_achievements = main.player.achievements

    list_of_achievements = []
    for achievement in achievements.keys():
        if gained_achievements and achievement in gained_achievements:
            list_of_achievements.insert(0, reached_card(achievements[achievement]))
        else:
            pass
            list_of_achievements.append(unreached_card(achievements[achievement]))

    return ft.AlertDialog(title = "Achievements", content = app.alignment("cstart", *list_of_achievements, spacing = tools.adapt_dimensions(app, "w", 4), expand = True), bgcolor = app.theme.background, actions = [ft.ElevatedButton("Okay", style = tools.ok_button_style(app, 14), on_click=lambda e: app.page.pop_dialog())], actions_alignment = ft.MainAxisAlignment.END, modal = True)

def loading_ui(app):
    app.add_element(app.alignment("rcenter", ft.Text("Build your life today!", style = tools.primary_text_style(app, 80)), width = tools.adapt_dimensions(app, "w", 100), spacing = tools.adapt_dimensions(app, "w", 4), expand = True))
    app.add_element(app.alignment("rcenter", ft.Text("We are preparing everything to begin your adventure...", style = tools.secondary_text_style(app, 18)), width = tools.adapt_dimensions(app, "w", 100), spacing = tools.adapt_dimensions(app, "w", 4), expand = True))

def register_page_1_ui(app):
    nickname = tools.entry(app, 14, label="Nickname", hint_text="How can we call you?", on_change=lambda: check())
    nickname_message = ft.Text("", style = tools.secondary_text_style(app, 12))
    
    date_picker = ft.DatePicker(last_date = utils.get_latest(), first_date = utils.get_earliest(), on_change=lambda: check())
    date_message = ft.Text(f"Please select your birthday", style = tools.secondary_text_style(app, 12))

    role = tools.dropdown(app, 12, label="Role", options=[tools.doption(app, option) for option in utils.get_roles().keys()], on_select=lambda: check())
    role_message = ft.Text("", style = tools.secondary_text_style(app, 12))
    status = tools.dropdown(app, 12, label="Status", options=[tools.doption(app, option) for option in utils.get_statuses().keys()], on_select=lambda: check())
    status_message = ft.Text("", style = tools.secondary_text_style(app, 12))

    next_step = ft.ElevatedButton("Continue", icon = utils.icon("continue_1"), width = tools.adapt_dimensions(app, "w", 40), style = tools.additional_button_style(app, 14), disabled=True, on_click=lambda: next_page())

    nickname.value = register_manager.get_first_part()[0]
    if register_manager.get_first_part()[1]:
        date_picker.value = register_manager.get_first_part()[1]
    role.value = register_manager.get_first_part()[2]
    status.value = register_manager.get_first_part()[3]

    app.add_element(app.alignment("cspace_between",
                        app.alignment("rcenter", ft.Text("Hi! To begin using this app\nwe need to meet you!", style = tools.primary_text_style(app, 24), text_align = ft.TextAlign.CENTER)),
                        app.alignment("rcenter", app.alignment("ccenter", nickname, nickname_message)),
                        app.alignment("rcenter", app.alignment("ccenter", ft.ElevatedButton("Select your birthday", icon = utils.icon("birthday"), style = tools.main_button_style(app, 14), on_click=lambda : app.page.show_dialog(date_picker)), date_message)),
                        app.alignment("rcenter", app.alignment("ccenter", role, role_message)),
                        app.alignment("rcenter", app.alignment("ccenter", status, status_message)),
                        app.alignment("rcenter", next_step),
                        width = tools.adapt_dimensions(app, "w", 100)))

    def check():
        nickname_valid = len(nickname.value) > 3 and len(nickname.value) < 20
        nickname_message.value = "" if nickname_valid else "Nickname must be between 3 and 20 characters"
        date_message.value = f"Your birthday is: {date_picker.value.astimezone():%Y-%m-%d}" if date_picker.value else "Please select your birthday"
        if nickname_valid and date_picker.value and role.value and status.value:
            next_step.disabled = False
            next_step.style = tools.main_button_style(app, 14)

        else:
            next_step.disabled = True
            next_step.style =  tools.additional_button_style(app, 14)
    

    def next_page():
        register_manager.set_first_part(nickname.value, date_picker.value, role.value, status.value)
        app.navigate("register_2")

    check()

def register_page_2_ui(app):
    height_label = ft.Text("Your height (in cm)", style = tools.primary_text_style(app, 16))
    height_value = ft.Text("100 cm", style = tools.secondary_text_style(app, 16), width = tools.adapt_dimensions(app, "w", 10), text_align = ft.TextAlign.END)
    height = tools.slider(app, min=100, max=200, divisions = 100, value = 100, label = "Height", on_change=lambda: check())
    weight = tools.entry(
        app, 14,
        label="Your weight (in kg)",
        hint_text="50.0",
        suffix="kg",
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^[0-9.]*$",
            replacement_string="",
        ),
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=lambda: on_weight_change(),
    )

    weight_message = ft.Text("", style = tools.secondary_text_style(app, 12))
    gender = tools.radio_group(app, tools.radio(app, 12, label="Male", value="male", width=tools.adapt_dimensions(app, "w", 10)), tools.radio(app, 12, label="Female", value="female", width=tools.adapt_dimensions(app, "w", 10)), on_change=lambda: check())
    gender_message = ft.Text("", style = tools.secondary_text_style(app, 12))
    next_step = ft.ElevatedButton("Continue", icon = utils.icon("continue_2"), width = tools.adapt_dimensions(app, "w", 40), style = tools.additional_button_style(app, 14), disabled=True, on_click=lambda: next_page())
    
    if register_manager.get_second_part()[0] != 0 and register_manager.get_second_part()[1] != 0.0 and register_manager.get_second_part()[2] != "":
        height.value = register_manager.get_second_part()[0]
        weight.value = register_manager.get_second_part()[1]
        gender.value = register_manager.get_second_part()[2]
        height_value.value = f"{int(height.value)} cm"

    app.add_element(app.alignment("cspace_between",
                        app.alignment("rcenter", ft.Text("Nice! Now we need to get information for\nsetting up individual goals...", style = tools.primary_text_style(app, 24), text_align = ft.TextAlign.CENTER)),
                        app.alignment("rcenter", height_label),
                        app.alignment("rcenter", height_value, height),
                        app.alignment("rcenter", app.alignment("ccenter", weight, weight_message)),
                        app.alignment("rcenter", app.alignment("ccenter", gender, gender_message)),
                        app.alignment("rcenter", next_step),
                        app.alignment("rspace_between", ft.IconButton(icon = utils.icon("return"), style = tools.additional_button_style(app, 10), on_click=lambda: app.navigate("register_1"))),
                        width = tools.adapt_dimensions(app, "w", 100)))

    WEIGHT_MIN = 20.0
    WEIGHT_MAX = 300.0

    def on_weight_change():
        val = weight.value

        if val.count(".") > 1:
            first_dot = val.find(".")
            val = val[:first_dot + 1] + val[first_dot + 1:].replace(".", "")

        if "." in val:
            whole, _, frac = val.partition(".")
            val = whole + "." + frac[:1]

        if val != weight.value:
            weight.value = val
            weight.update()

        check()

    def check():
        height_value.value = f"{int(height.value)} cm"
        weight_message.value = ""
        gender_message.value = ""
        weight_val = weight.value.strip() if weight.value else ""

        if not weight_val or weight_val == ".":
            weight_message.value = "Please enter a valid weight"
        else:
            try:
                num = float(weight_val)
                if not (WEIGHT_MIN <= num <= WEIGHT_MAX):
                    weight_message.value = f"Enter a weight between {WEIGHT_MIN:.0f} and {WEIGHT_MAX:.0f} kg"
                elif not gender.value:
                    gender_message.value = "Please select a gender"
                else:
                    next_step.disabled = False
                    next_step.style = tools.main_button_style(app, 14)
            except ValueError:
                weight_message.value = "Please enter a valid weight"
    
    def next_page():
        register_manager.set_second_part(height.value, weight.value, gender.value)
        app.navigate("register_3")

    check()

def register_page_3_ui(app):
    activity_label = ft.Text("How can you evaluate your activeness during last month?", style = tools.primary_text_style(app, 16))
    activity_value = ft.Text("0%", style = tools.secondary_text_style(app, 16), width = tools.adapt_dimensions(app, "w", 10), text_align = ft.TextAlign.END)
    activity = tools.slider(app, min=0, max=100, divisions = 100, value = 0, label = "Activity", on_change=lambda: check())


    preferences=utils.get_available_preferences()
    chosen_preferences = []
    preferences_label = ft.Text("Select your preferences (at least 3)", style = tools.primary_text_style(app, 16))

    preferences_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                name, style = tools.additional_button_style(app, 12),
                on_click=lambda e, name=name: preferences_click(e, name),
            )
            for name in preferences.keys()
        ],
        wrap=True,
        spacing=10,
        run_spacing=10,
    )

    preferences_column = ft.Column(
        controls=[preferences_row],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )

    preferences_list = ft.Container(
        bgcolor=app.theme.additional_color,
        border_radius=10,
        width=tools.adapt_dimensions(app, "w", 60),
        height=tools.adapt_dimensions(app, "h", 20),
        padding=10,
        content=preferences_column,
    )


    skills=utils.get_available_skills()
    chosen_skills = []
    skills_label = ft.Text("Select your skills (at least 3)", style = tools.primary_text_style(app, 16))

    skills_row = ft.Row(
        controls=[
            ft.ElevatedButton(
                name, style = tools.additional_button_style(app, 12),
                on_click=lambda e, name=name: skill_click(e, name),
            )
            for name in skills.keys()
        ],
        wrap=True,
        spacing=10,
        run_spacing=10,
    )

    skills_column = ft.Column(
        controls=[skills_row],
        scroll=ft.ScrollMode.AUTO,
        spacing=10,
    )

    skills_list = ft.Container(
        bgcolor=app.theme.additional_color,
        border_radius=10,
        width=tools.adapt_dimensions(app, "w", 60),
        height=tools.adapt_dimensions(app, "h", 20),
        padding=10,
        content=skills_column,
    )

    terms_and_conditions_checkbox = tools.checkbox(app, 12, label="I agree to the terms and conditions", on_change=lambda: check())
    data_agreement_checkbox = tools.checkbox(app, 12, label="I allow to use my data", on_change=lambda: check())

    next_step = ft.ElevatedButton("Finish", icon=utils.icon("finish"), width = tools.adapt_dimensions(app, "w", 40), style = tools.additional_button_style(app, 14), disabled=True, on_click=lambda: next_page())
    
    app.add_element(app.alignment("cspace_between",
                        app.alignment("rcenter", ft.Text("The last, but not least...\n We also need to know more about your skills, preferences and so on...!", style = tools.primary_text_style(app, 24), text_align = ft.TextAlign.CENTER)),
                        app.alignment("rcenter", activity_label),
                        app.alignment("rcenter", activity_value, activity),
                        app.alignment("rcenter", preferences_label),
                        app.alignment("rcenter", preferences_list),
                        app.alignment("rcenter", skills_label),
                        app.alignment("rcenter", skills_list),
                        app.alignment("rcenter", terms_and_conditions_checkbox),
                        app.alignment("rcenter", data_agreement_checkbox),
                        app.alignment("rcenter", next_step),
                        app.alignment("rspace_between", ft.IconButton(icon = utils.icon("return"), style = tools.additional_button_style(app, 10), on_click=lambda: app.navigate("register_2"))),
                        width = tools.adapt_dimensions(app, "w", 100)))

    def preferences_click(e, name):
        if name in chosen_preferences:
            chosen_preferences.remove(name)
            e.control.style = tools.additional_button_style(app, 12)
        else:
            chosen_preferences.append(name)
            e.control.style = tools.main_button_style(app, 16)
        check()


    def skill_click(e, name):
        if name in chosen_skills:
            chosen_skills.remove(name)
            e.control.style = tools.additional_button_style(app, 12)
        else:
            chosen_skills.append(name)
            e.control.style = tools.main_button_style(app, 16)
        check()

    def check():
        activity_value.value = f"{int(activity.value)}%"
        if len(chosen_preferences) >= 3 and len(chosen_skills) >= 3 and terms_and_conditions_checkbox.value and data_agreement_checkbox.value:
            next_step.disabled = False
            next_step.style = tools.main_button_style(app, 14)
        else:
            next_step.disabled = True
            next_step.style = tools.additional_button_style(app, 14)
    
    def next_page():
        register_manager.set_thirds_part(activity_value.value, chosen_preferences, chosen_skills)
        app.page.run_task(main.finish_registration, app)

    check()

def goal_page(app):
    def page_back():
        main.open_goal = None
        app.navigate("main_page")

    def increase(entry, type):
        if type == "amount":
            entry.value = int(entry.value) + 1
        elif type == "time":
            entry.value = utils.add_time(entry.value, "12:00:00")

    def decrease(entry, type):
        if type == "amount" and int(entry.value)>0:
            entry.value = int(entry.value) - 1
        elif type == "time":
            entry.value = utils.remove_time(entry.value, "00:00:00")
            
    goal = main.open_goal
    if isinstance(goal.goal, ActionGoal):
        cat = 1
    elif isinstance(goal.goal, AmountGoal):
        cat = 2
    elif isinstance(goal.goal, TimeGoal):
        cat = 3
    else:
        return ValueError("Invalid goal")

    def complete():
        if isinstance(goal.goal, ActionGoal):
            result = main.player.complete_goal(goal) 
        else:
            result = main.player.complete_goal(goal, entry.value) 

        if not result:
            app.navigate("main_page")
        else:
            main.last_completed = result
            app.page.run_task(main.save_stats, app)
            app.page.run_task(main.save_goals, app)
            app.navigate("completement_page")

    if cat == 1:
        goal_comletement = app.alignment("rcenter", 
                            ft.Button(content = "Complete", 
                                style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                width = tools.adapt_dimensions(app, "w", 60),
                                height = tools.adapt_dimensions(app, "w", 8),
                                on_click = complete), width = tools.adapt_dimensions(app, "w", 100))

    elif cat == 2:
        entry = tools.entry(app, 24, value = 0, keyboard_type = ft.KeyboardType.NUMBER, width = tools.adapt_dimensions(app, "w", 20), height = tools.adapt_dimensions(app, "w", 8), suffix = goal.goal.unit)
        goal_comletement = app.alignment("cstart", app.alignment("rcenter",
                            ft.IconButton(icon = utils.icon("controls_decrease"), style = tools.cancel_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: decrease(entry, "amount")),
                            entry,
                            ft.IconButton(icon = utils.icon("controls_increase"), style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: increase(entry, "amount")),
                                expand = True),
                                app.alignment("rcenter", 
                                    ft.Button(content = "Complete", 
                                    style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                    width = tools.adapt_dimensions(app, "w", 60),
                                    height = tools.adapt_dimensions(app, "w", 8),
                                    on_click = complete), width = tools.adapt_dimensions(app, "w", 100)))

    if cat == 3:
        entry = tools.entry(app, 24, value = "00:00:00", width = tools.adapt_dimensions(app, "w", 20), height = tools.adapt_dimensions(app, "w", 8))
        goal_comletement = app.alignment("cstart", app.alignment("rcenter",
                            ft.IconButton(icon = utils.icon("controls_decrease"), style = tools.cancel_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: decrease(entry, "time")),
                            entry,
                            ft.IconButton(icon = utils.icon("controls_increase"), style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: increase(entry, "time")),
                                expand = True),
                                app.alignment("rcenter", 
                                    ft.Button(content = "Complete", 
                                    style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                    width = tools.adapt_dimensions(app, "w", 60),
                                    height = tools.adapt_dimensions(app, "w", 8),
                                    on_click = complete), width = tools.adapt_dimensions(app, "w", 100)))    

    app.add_element(app.alignment("cstart",
                    app.alignment("rstart", ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, width = tools.adapt_dimensions(app, "h", 10), height = tools.adapt_dimensions(app, "h", 10), style=tools.main_button_style(app, 8), padding=5, on_click = page_back)),
                    app.alignment("rcenter", ft.Text(goal.goal.title, style = tools.primary_text_style(app, 48))),
                    app.alignment("rcenter", ft.Container(
                        content = ft.Text(goal.goal.description, style = tools.secondary_text_style(app, 22)),
                        bgcolor = app.theme.entry,
                        padding = tools.adapt_dimensions(app, "w", 5),
                        border_radius = 10,
                        width = tools.adapt_dimensions(app, "w", 90),
                        height = tools.adapt_dimensions(app, "h", 20))),
                    goal_comletement,
                    ))

def goals_config_page(app):
    action_goals, amount_goals, time_goals = main.action_goals, main.amount_goals, main.time_goals
    all_pool_goals = action_goals + amount_goals + time_goals

    state = {
        "mode": None,
        "template_goal": None,
        "period_goal": None,
        "period_list": None,
        "period": None,
        "target_value": None,
        "custom_finish": None,
    }
    period_buttons = {}
    preset_buttons = {}

    active_column = ft.Column()
    dialog_body = ft.Column()
    dialog = ft.AlertDialog(title=ft.Text(""), bgcolor = app.theme.background, content=dialog_body, actions=[])

    def rebuild_active_column(push_update=True):
        rows = []
        for pg, lst in [(g, main.player.daily_goals) for g in main.player.daily_goals] + \
                        [(g, main.player.weekly_goals) for g in main.player.weekly_goals] + \
                        [(g, main.player.custom_goals) for g in main.player.custom_goals]:

            delete_btn = ft.ElevatedButton("Delete", style = tools.cancel_button_style(app, 22), on_click=lambda e, pg=pg, lst=lst: delete_goal(pg, lst))

            edit_btn = ft.Container(width = 0, height = 0)

            if isinstance(pg, DailyGoal): goal_period = "Daily"
            elif isinstance(pg, WeeklyGoal): goal_period = "Weekly"
            else: goal_period = "Ends on " + pg.finish_time.strftime("%m-%d %H:%M:%S")

            if not isinstance(pg.goal, ActionGoal):
                
                if isinstance(pg.goal, AmountGoal): number = pg.goal.target_amount
                else: number = str(pg.goal.target_duration)

                edit_btn = ft.ElevatedButton("Edit", style = tools.additional_button_style(app, 22), on_click=lambda e, pg=pg, lst=lst: open_edit_dialog(pg, lst))
                goal_item = app.alignment("cspace_between", app.alignment("rcenter",
                                                ft.Text(goal_period, style = tools.secondary_text_style(app, 18)),
                                                ft.Text(pg.goal.title, style = tools.primary_text_style(app, 36)),
                                                ft.Text(number, style = tools.secondary_text_style(app, 18)),
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ), app.alignment("rstart",
                                                ft.Text(pg.goal.description, style = tools.secondary_text_style(app, 24)),
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ), app.alignment("rspace_evenly",
                                                edit_btn, delete_btn,
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ),
                                            width = tools.adapt_dimensions(app, "w", 80),
                                            height = tools.adapt_dimensions(app, "h", 40))

            else:
                goal_item = app.alignment("cspace_between", app.alignment("rcenter",
                                                ft.Text(goal_period, style = tools.secondary_text_style(app, 18)),
                                                ft.Text(pg.goal.title, style = tools.primary_text_style(app, 36)),
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ), app.alignment("rstart",
                                                ft.Text(pg.goal.description, style = tools.secondary_text_style(app, 24)),
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ), app.alignment("rspace_evenly",
                                                delete_btn,
                                                width = tools.adapt_dimensions(app, "w", 80)
                                            ),
                                            width = tools.adapt_dimensions(app, "w", 80),
                                            height = tools.adapt_dimensions(app, "h", 40))                

            rows.append(ft.Container(content = goal_item,
                            bgcolor = app.theme.additional_color,
                            border_radius = 10,
                            width = tools.adapt_dimensions(app, "w", 90),
                            height = tools.adapt_dimensions(app, "h", 40), 
                            padding = tools.adapt_dimensions(app, "w", 5)))

        active_column.controls = rows
        if push_update:
            active_column.update()

    def delete_goal(pg, lst):
        lst.remove(pg)
        rebuild_active_column()
        app.page.run_task(main.save_goals, app)

    def make_period_button(period, label):
        btn = ft.ElevatedButton(
            label,
            on_click=lambda e: select_period(period),
            style=tools.main_button_style(app, 14) if state["period"] == period else tools.additional_button_style(app, 14),
        )
        period_buttons[period] = btn
        return btn

    def select_period(period):
        state["period"] = period
        rebuild_dialog_body()

    def make_preset_button(value, label):
        btn = ft.ElevatedButton(
            label,
            on_click=lambda e: select_preset(value),
            style=tools.main_button_style(app, 14) if state["target_value"] == value else tools.additional_button_style(app, 14),
        )
        preset_buttons[value] = btn
        return btn

    def select_preset(value):
        state["target_value"] = value
        for v, btn in preset_buttons.items():
            btn.style = tools.main_button_style(app, 14) if v == value else tools.additional_button_style(app, 14)
        dialog_body.update()

    def on_custom_date_change(e):
        picked = e.control.value.astimezone()
        state["custom_finish"] = datetime.combine(picked.date(), time.max)

    def on_target_change(e):
        try:
            state["target_value"] = float(e.control.value)
        except ValueError:
            state["target_value"] = None

    def select_template_goal(title):
        for g in all_pool_goals:
            if g.title == title:
                state["template_goal"] = g
                break
        state["period"] = None
        state["target_value"] = None
        state["custom_finish"] = None
        period_buttons.clear()
        preset_buttons.clear()
        rebuild_dialog_body()

    def rebuild_dialog_body():
        controls = []
        goal = state["template_goal"]

        if state["mode"] == "create":
            dropdown = tools.dropdown(app, 14, label="Select a goal",
                                        options=[tools.doption(app, g.title) for g in all_pool_goals],
                                        on_select=lambda e: select_template_goal(e.control.value))
            controls.append(dropdown)

        if goal is not None:
            if state["mode"] == "create":
                row = []
                if goal.available_periods.get("daily"):
                    row.append(make_period_button("daily", "Daily"))
                if goal.available_periods.get("weekly"):
                    row.append(make_period_button("weekly", "Weekly"))
                if goal.available_periods.get("custom"):
                    row.append(make_period_button("custom", "Custom"))
                controls.append(app.alignment("rstart", *row, width=tools.adapt_dimensions(app, "w", 100)))

            period = state["period"] if state["mode"] == "create" else type(state["period_goal"]).__name__.replace("Goal", "").lower()

            if period == "custom":
                date_picker = ft.DatePicker(on_change=on_custom_date_change)
                app.page.overlay.append(date_picker)
                controls.append(ft.ElevatedButton("Pick finish date", style = tools.main_button_style(app, 14), on_click=lambda e: app.open_dialog(date_picker)))

            if isinstance(goal, AmountGoal):
                if goal.input_mode == InputMode.PRESET:
                    preset_buttons.clear()
                    preset_row = [make_preset_button(v, f"{v} {goal.unit}") for v in goal.preset_options]
                    controls.append(app.alignment("rstart", *preset_row, width=tools.adapt_dimensions(app, "w", 100)))
                else:
                    controls.append(ft.TextField(label=f"Target amount ({goal.unit})",
                                                  value=str(goal.target_amount), on_change=on_target_change))

            elif isinstance(goal, TimeGoal) and goal.user_defined_target:
                if goal.input_mode == InputMode.PRESET:
                    preset_buttons.clear()
                    preset_row = [make_preset_button(v, f"{v} min") for v in goal.preset_options]
                    controls.append(app.alignment("rstart", *preset_row, width=tools.adapt_dimensions(app, "w", 100)))
                else:
                    minutes = int(goal.target_duration.total_seconds() // 60)
                    controls.append(ft.TextField(label="Target time (minutes)",
                                                  value=str(minutes) if minutes else "", on_change=on_target_change))

        dialog_body.controls = controls
        dialog.actions = [
            ft.ElevatedButton("Cancel", style = tools.cancel_button_style(app, 14), on_click=lambda e: app.page.pop_dialog()),
            ft.ElevatedButton("Save", style = tools.ok_button_style(app, 14), on_click=lambda e: confirm_dialog()),
        ]
        dialog.title = ft.Text("Create goal" if state["mode"] == "create" else "Edit goal")
        try:
            dialog.update()
        except Exception:
            pass

    def open_create_dialog(e=None):
        state["mode"] = "create"
        state["template_goal"] = None
        state["period_goal"] = None
        state["period_list"] = None
        state["period"] = None
        state["target_value"] = None
        state["custom_finish"] = None
        period_buttons.clear()
        preset_buttons.clear()
        rebuild_dialog_body()
        app.open_dialog(dialog)

    def open_edit_dialog(pg, lst):
        state["mode"] = "edit"
        state["period_goal"] = pg
        state["period_list"] = lst
        state["template_goal"] = pg.goal
        state["period"] = None
        state["target_value"] = None
        state["custom_finish"] = None
        preset_buttons.clear()
        rebuild_dialog_body()
        app.open_dialog(dialog)

    def confirm_dialog():
        if state["mode"] == "create":
            add_goal()
        else:
            apply_edit()
        app.page.pop_dialog()
        rebuild_active_column()
        app.page.run_task(main.save_goals, app)

    def add_goal():
        goal = state["template_goal"]
        period = state["period"]
        if goal is None or period is None:
            return

        new_goal = copy.deepcopy(goal)

        if isinstance(new_goal, AmountGoal) and state["target_value"] is not None:
            new_goal.target_amount = state["target_value"]
        elif isinstance(new_goal, TimeGoal) and new_goal.user_defined_target and state["target_value"] is not None:
            new_goal.target_duration = timedelta(minutes=state["target_value"])

        if period == "daily":
            main.player.daily_goals.append(DailyGoal(goal=new_goal))
        elif period == "weekly":
            main.player.weekly_goals.append(WeeklyGoal(goal=new_goal))
        elif period == "custom":
            if state["custom_finish"] is None:
                return
            main.player.custom_goals.append(CustomGoal(
                goal=new_goal, assigned_time=datetime.now(), finish_time=state["custom_finish"]))

    def apply_edit():
        goal = state["period_goal"].goal

        if isinstance(goal, AmountGoal) and state["target_value"] is not None:
            goal.target_amount = state["target_value"]
        elif isinstance(goal, TimeGoal) and goal.user_defined_target and state["target_value"] is not None:
            goal.target_duration = timedelta(minutes=state["target_value"])

        if isinstance(state["period_goal"], CustomGoal) and state["custom_finish"] is not None:
            state["period_goal"].finish_time = state["custom_finish"]

    rebuild_active_column(push_update=False)
    app.add_element(app.alignment("cstart",
                                app.alignment("rstart", ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, width = tools.adapt_dimensions(app, "h", 10), height = tools.adapt_dimensions(app, "h", 10), style=tools.main_button_style(app, 8), padding=5, on_click = lambda: app.navigate("main_page"))),
                                active_column,
                                ft.ElevatedButton("Create goal", style = tools.ok_button_style(app, 14), on_click=open_create_dialog),
                                width=tools.adapt_dimensions(app, "w", 100)))

def completement_page(app):
    completed = main.last_completed
    results = []
    for result in completed.keys():
        if completed[result]>0:
            results.append(ft.Text(f"{result}: +{completed[result]}", color = app.theme.ok_button, size = 18))
        elif completed[result]<0:
            results.append(ft.Text(f"{result}: {completed[result]}", color = app.theme.cancel_button, size = 18))
    end_btn = ft.Button(content = "Done", 
                                            style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                            width = tools.adapt_dimensions(app, "w", 60),
                                            height = tools.adapt_dimensions(app, "w", 8),
                                            on_click = lambda: app.navigate("main_page"))
    
    app.add_element(app.alignment("rcenter", ft.Text("Task completed", style = tools.primary_text_style(app, 32)), width = tools.adapt_dimensions(app, "w", 100)))
    app.add_element(app.alignment("cstart", *results, width = tools.adapt_dimensions(app, "w", 100), height = tools.adapt_dimensions(app, "h", 65), spacing = tools.adapt_dimensions(app, "w", 4)))
    app.add_element(app.alignment("rcenter", end_btn, width = tools.adapt_dimensions(app, "w", 100)))

def task_page(app):

    selected_options = []
    option_buttons = {}

    def page_back():
        parts = main.current_path.split("/")
        parent = "/".join(parts[:-1])

        main.current_path = parent
        app.navigate("tasks_navigation_page")

    def make_button(key):
        return ft.Button(
            content=ft.Text(key.capitalize(), style=tools.secondary_text_style(app, 50, weight=ft.FontWeight.BOLD)),
            style=tools.additional_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
            width=tools.adapt_dimensions(app, "w", 30),
            height=tools.adapt_dimensions(app, "w", 30),
            on_click=lambda e, k=key: on_option_tap(k),
        )

    def make_input(key, unit):
            return ft.Button(
                f"{key.capitalize()} {unit}",
                style=tools.ok_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
                width=tools.adapt_dimensions(app, "w", 20),
                height=tools.adapt_dimensions(app, "w", 20),
                on_click=lambda: complete(key),
            )

    def on_option_tap(key):
        if task.additional_options_select == "multiple":
            if key in selected_options:
                selected_options.remove(key)
                option_buttons[key].style = tools.additional_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10))
            else:
                selected_options.append(key)
                option_buttons[key].style = tools.main_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
        else:
            for prev_key in selected_options:
                option_buttons[prev_key].style = tools.additional_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10))
            selected_options.clear()
            selected_options.append(key)
            option_buttons[key].style = tools.main_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10))

    def increase(entry, type, max):
        if type == "amount" and int(entry.value)<max:
            entry.value = int(entry.value) + 1
        elif type == "time":
            entry.value = utils.add_time(entry.value, max)

    def decrease(entry, type, min):
        if type == "amount" and int(entry.value)>min:
            entry.value = int(entry.value) - 1
        elif type == "time":
                    entry.value = utils.remove_time(entry.value, min)
            

    task = utils.get_node(main.current_path, main.tasks)
    if isinstance(task, ActionTask):
        cat = 1
    elif isinstance(task, AmountTask):
        cat = 2
        input_mode = task.amount_input_mode
    elif isinstance(task, TimeTask):
        cat = 3
        input_mode = task.time_input
    else:
        return ValueError("Invalid task")

    additional_options_selector = []
    if task.additional_options:
        opt = list(task.additional_options.keys())
        rows = [opt[i : i + 3] for i in range(0, len(opt), 3)]
        for row in rows:
            row_buttons = []
            for key in row:
                btn = make_button(key)
                option_buttons[key] = btn
                row_buttons.append(btn)
            additional_options_selector.append(app.alignment("rcenter",
                *row_buttons,
                spacing=tools.adapt_dimensions(app, "w", 4)))     

    def complete(option = ""):
        if cat == 1:
            result = main.player.action_task(task, selected_options)
        elif cat == 2:
            if input_mode == "preset":
                result = main.player.amount_task(task, option, selected_options)
            else:
                result = main.player.amount_task(task, int(entry.value), selected_options)
        elif cat == 3:
            if input_mode == "preset":
                result = main.player.time_task(task, option, selected_options)
            else:
                result = main.player.time_task(task, entry.value, selected_options)

        if not result:
            pass
        else:
            main.last_completed = result
            app.page.run_task(main.save_stats, app)
            app.navigate("completement_page")


    if cat == 1:
        task_comletement = app.alignment("rcenter", 
                                        ft.Button(content = "Complete", 
                                        style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                        width = tools.adapt_dimensions(app, "w", 60),
                                        height = tools.adapt_dimensions(app, "w", 8),
                                        on_click = complete), width = tools.adapt_dimensions(app, "w", 100))

    elif cat == 2:
        if input_mode == "free":
            entry = tools.entry(app, 24, value = task.min, keyboard_type = ft.KeyboardType.NUMBER, width = tools.adapt_dimensions(app, "w", 20), height = tools.adapt_dimensions(app, "w", 8), suffix = task.units.split("/")[1])
            task_comletement = app.alignment("cstart", app.alignment("rcenter",
                                    ft.IconButton(icon = utils.icon("controls_decrease"), style = tools.cancel_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: decrease(entry, "amount", task.min)),
                                    entry,
                                    ft.IconButton(icon = utils.icon("controls_increase"), style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: increase(entry, "amount", task.max)),
                                expand = True),
                                    app.alignment("rcenter", 
                                        ft.Button(content = "Complete", 
                                        style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                        width = tools.adapt_dimensions(app, "w", 60),
                                        height = tools.adapt_dimensions(app, "w", 8),
                                        on_click = complete), width = tools.adapt_dimensions(app, "w", 100)))

        if input_mode == "preset":
            Input_options = []
            Inputs = list(task.amount_inputs_multipliers.keys())
            rows = [Inputs[i : i + 3] for i in range(0, len(Inputs), 3)]
            for row in rows:
                row_buttons = []
                for key in row:
                    if key == "1":
                        unit = task.units.split("/")[0]
                    else:
                        unit = task.units.split("/")[1]
                    btn = make_input(key, unit)
                    option_buttons[key] = btn
                    row_buttons.append(btn)
                Input_options.append(app.alignment("rcenter",
                    *row_buttons,
                    spacing=tools.adapt_dimensions(app, "w", 4)))
            task_comletement = app.alignment("cstart", *Input_options,
                width=tools.adapt_dimensions(app, "w", 100),
                spacing=tools.adapt_dimensions(app, "w", 4), expand=True)

    if cat == 3:
        if input_mode == "free":
            entry = tools.entry(app, 24, value = task.min, width = tools.adapt_dimensions(app, "w", 20), height = tools.adapt_dimensions(app, "w", 8))
            task_comletement = app.alignment("cstart", app.alignment("rcenter",
                                    ft.IconButton(icon = utils.icon("controls_decrease"), style = tools.cancel_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: decrease(entry, "time", task.min)),
                                    entry,
                                    ft.IconButton(icon = utils.icon("controls_increase"), style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)), width = tools.adapt_dimensions(app, "w", 8), height = tools.adapt_dimensions(app, "w", 8), on_click = lambda: increase(entry, "time", task.max)),
                                expand = True),
                                    app.alignment("rcenter", 
                                        ft.Button(content = "Complete", 
                                        style = tools.ok_button_style(app, 28, shape=ft.RoundedRectangleBorder(radius=10)),
                                        width = tools.adapt_dimensions(app, "w", 60),
                                        height = tools.adapt_dimensions(app, "w", 8),
                                        on_click = complete), width = tools.adapt_dimensions(app, "w", 100)))

        if input_mode == "preset":
            Input_options = []
            Inputs = list(task.time_inputs_multipliers.keys())
            rows = [Inputs[i : i + 3] for i in range(0, len(Inputs), 3)]
            for row in rows:
                row_buttons = []
                for key in row:
                    btn = make_input(key, "")
                    option_buttons[key] = btn
                    row_buttons.append(btn)
                Input_options.append(app.alignment("rcenter",
                    *row_buttons,
                    spacing=tools.adapt_dimensions(app, "w", 4)))
            task_comletement = app.alignment("cstart", *Input_options,
                width=tools.adapt_dimensions(app, "w", 100),
                spacing=tools.adapt_dimensions(app, "w", 4), expand=True)        
            

    app.add_element(app.alignment("cstart",
                    app.alignment("rstart", ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, width = tools.adapt_dimensions(app, "h", 10), height = tools.adapt_dimensions(app, "h", 10), style=tools.main_button_style(app, 8), padding=5, on_click = page_back)),
                    app.alignment("rcenter", ft.Text(task.title, style = tools.primary_text_style(app, 48))),
                    app.alignment("rcenter", ft.Container(
                        content = ft.Text(task.description, style = tools.secondary_text_style(app, 22)),
                        bgcolor = app.theme.entry,
                        padding = tools.adapt_dimensions(app, "w", 5),
                        border_radius = 10,
                        width = tools.adapt_dimensions(app, "w", 90),
                        height = tools.adapt_dimensions(app, "h", 20))),
                    app.alignment("cstart", *additional_options_selector,
                         width=tools.adapt_dimensions(app, "w", 100),
                         spacing=tools.adapt_dimensions(app, "w", 4), expand=True),
                    task_comletement,
                    ))

def tasks_navigation_ui(app):
    path = main.current_path
    node = utils.get_node(path, main.tasks) if path else main.tasks
    categories = list(node.keys())
    rows = [categories[i : i + 2] for i in range(0, len(categories), 2)]

    def page_back():
        parts = main.current_path.split("/")
        parent = "/".join(parts[:-1])

        if path == "":
            main.current_path = ""
            app.navigate("main_page")

        else:
            main.current_path = parent
            app.navigate("tasks_navigation_page")

    def on_tap(key):
        child = node[key]
        if isinstance(child, Task):
            main.current_path = f"{path}/{key}" if path else key
            app.navigate("task_page")
        else:
            main.current_path = f"{path}/{key}" if path else key
            app.navigate("tasks_navigation_page")

    def make_button(key, width):
        icon_key = f"{key}-task" if isinstance(node[key], Task) else key
        try:
            icon = utils.icon(icon_key)
            content = app.alignment("ccenter",
                ft.Icon(icon, color=app.theme.secondary, size=tools.adapt_dimensions(app, "w", 20)),
                ft.Text(key.capitalize(), style=tools.secondary_text_style(app, 50, weight=ft.FontWeight.BOLD)))
        except Exception:
            content = app.alignment("ccenter",
                ft.Text(key.capitalize(), style=tools.secondary_text_style(app, 50, weight=ft.FontWeight.BOLD)))

        return ft.Button(
            content=content,
            style=tools.additional_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
            width=tools.adapt_dimensions(app, "w", width),
            height=tools.adapt_dimensions(app, "w", 46),
            on_click=lambda e, k=key: on_tap(k),
        )

    buttons = []
    for row in rows:
        if len(row) > 1:
            buttons.append(app.alignment("rcenter",
                make_button(row[0], 46), make_button(row[1], 46),
                expand=True, spacing=tools.adapt_dimensions(app, "w", 4)))
        else:
            buttons.append(app.alignment("rcenter",
                make_button(row[0], 92),
                expand=True, spacing=tools.adapt_dimensions(app, "w", 4)))

    app.add_element(app.alignment("cstart", 
                        app.alignment("rstart", ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, width = tools.adapt_dimensions(app, "h", 10), height = tools.adapt_dimensions(app, "h", 10), style=tools.main_button_style(app, 8), padding=5, on_click = page_back)),
                        *buttons,
                     width=tools.adapt_dimensions(app, "w", 100),
                     spacing=tools.adapt_dimensions(app, "w", 4), expand=True))
    
def main_ui(app):

    def stats_element(name, stats):
        return app.alignment("rstart", ft.Icon(utils.icon(name+"-stat"), color=app.theme.primary, size=tools.adapt_dimensions(app, "w", 5)), ft.Text(name.capitalize()+":", style = tools.primary_text_style(app, 18)), ft.Text(str(round(stats)), style = tools.primary_text_style(app, 24, weight=ft.FontWeight.BOLD, italic=True)))

    def to_tasks():
        main.current_path=""
        app.navigate("tasks_navigation_page")

    def open_goal(goal):
        main.open_goal = goal
        app.navigate("goal_page")
        
    async def active_goals_tick_loop(app):
        while True:
            for goal, text_ctrl in main.active_goal_time_refs:
                if isinstance(goal, DailyGoal):
                    text_ctrl.value = utils.format_time_left_hours(goal.finish_time)
                else:
                    text_ctrl.value = utils.format_time_left_days(goal.finish_time)
                text_ctrl.update()
            await asyncio.sleep(1)

    def active_goals(app):
        active = main.player.daily_goals + main.player.weekly_goals + main.player.custom_goals
        if not active:
            return []

        goals_elements = []
        main.active_goal_time_refs.clear()

        for goal in active:
            resets_in_text = ft.Text("",
                                    style=tools.primary_text_style(app, 35, weight=ft.FontWeight.BOLD))

            if goal.goal.status == GoalStatus.IN_PROGRESS:
                goal_control = ft.Button("Proceed to goal", style = tools.ok_button_style(app, 32), width = tools.adapt_dimensions(app, "w", 30), height = tools.adapt_dimensions(app, "h", 15), on_click = lambda e, g=goal: open_goal(g))

            elif goal.goal.status == GoalStatus.COMPLETED:
                goal_control = ft.Text("Completed", color = app.theme.ok_button)

            main.active_goal_time_refs.append((goal, resets_in_text))

            if isinstance(goal.goal, ActionGoal):
                goal_ui = app.alignment("cstart",
                            app.alignment("rspace_between",
                                ft.Text(goal.goal.title, style=tools.primary_text_style(app, 40)),
                                resets_in_text,
                                width=tools.adapt_dimensions(app, "w", 80)),
                            app.alignment("rstart", 
                                ft.Text(goal.goal.description, style=tools.secondary_text_style(app, 20))),
                            app.alignment("rend", goal_control, width = tools.adapt_dimensions(app, "w", 80))
                        )

            elif isinstance(goal.goal, AmountGoal):
                goal_ui = app.alignment("cstart",
                            app.alignment("rspace_between",
                                ft.Text(goal.goal.title, style=tools.primary_text_style(app, 40)),
                                resets_in_text,
                                width=tools.adapt_dimensions(app, "w", 80)),
                            app.alignment("rstart", ft.Text(goal.goal.description, style=tools.secondary_text_style(app, 20))),
                            app.alignment("rspace_between",
                                ft.Column(alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.END, 
                                    controls = [
                                        tools.progress_bar(app, width=tools.adapt_dimensions(app, "w", 50), height=tools.adapt_dimensions(app, "h", 7), value=goal.goal.progress()),
                                        ft.Text(f"{goal.goal.current_amount}/{goal.goal.target_amount} {goal.goal.unit}", style=tools.secondary_text_style(app, 20))]),
                                goal_control)
                        )

            elif isinstance(goal.goal, TimeGoal):
                goal_ui = app.alignment("cstart",
                            app.alignment("rspace_between",
                                ft.Text(goal.goal.title, style=tools.primary_text_style(app, 40)),
                                resets_in_text,
                                width=tools.adapt_dimensions(app, "w", 80)),
                            app.alignment("rstart", ft.Text(goal.goal.description, style=tools.secondary_text_style(app, 20))),
                            app.alignment("rspace_between",
                                ft.Column(alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.END, 
                                    controls = [
                                        tools.progress_bar(app, width=tools.adapt_dimensions(app, "w", 50), height=tools.adapt_dimensions(app, "h", 7), value=goal.goal.progress()),
                                        ft.Text(f"{goal.goal.accumulated}/{goal.goal.target_duration}", style=tools.secondary_text_style(app, 30))]),
                                goal_control)                            
                        )

            goals_elements.append(ft.Container(
                                        content=goal_ui,
                                        bgcolor=app.theme.additional_color,
                                        border_radius=10,
                                        padding=tools.adapt_dimensions(app, "w", 5),
                                        width=tools.adapt_dimensions(app, "w", 90),
                                        height=tools.adapt_dimensions(app, "h", 40),
                                    ))

        return goals_elements

    app.page.run_task(active_goals_tick_loop, app)

    level_stat = app.alignment("rstart",
        ft.Button(
            content = ft.Text(
                str(main.player.level),
                style = tools.primary_text_style(app, 50)),
            bgcolor=app.theme.additional_color, 
            style=ft.ButtonStyle(shape=ft.CircleBorder(),
            side = ft.BorderSide(5, color=app.theme.ok_button),
            alignment=ft.Alignment.CENTER)),
        ft.Column(alignment = ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.END,
            controls = [tools.progress_bar(app, width=tools.adapt_dimensions(app, "w", 35), height=tools.adapt_dimensions(app, "h", 6), value = main.player.experience / utils.get_required_exp(main.player.level + 1)),
            ft.Text(f"{round(main.player.experience)}/{utils.get_required_exp(main.player.level + 1)} exp", style = tools.primary_text_style(app, 12))]))
    
    health_stat = app.alignment("rstart",
        ft.Icon(utils.icon("health-stat"), color=app.theme.ok_button, size=tools.adapt_dimensions(app, "w", 6)),
        tools.progress_bar(app, width=tools.adapt_dimensions(app, "w", 25), height=tools.adapt_dimensions(app, "h", 5), value = main.player.experience / utils.get_required_exp(main.player.level + 1)),
        ft.Text(str(round(main.player.health)), style = tools.primary_text_style(app, 28)))
    
    player_card = ft.Container(content = app.alignment("cspace_evenly", 
                                            app.alignment("rcenter", level_stat, health_stat, spacing = tools.adapt_dimensions(app, "w", 15)), 
                                            app.alignment("rspace_between", 
                                                stats_element("creativity", main.player.creativity), 
                                                stats_element("intelligence", main.player.intelligence), 
                                                stats_element("social", main.player.social), 
                                                stats_element("strength", main.player.strength),
                                                width = tools.adapt_dimensions(app, "w", 85)),
                                                
                                            app.alignment("rspace_between", 
                                                stats_element("energy", main.player.energy), 
                                                stats_element("mood", main.player.mood), 
                                                stats_element("stress", main.player.stress),
                                                width = tools.adapt_dimensions(app, "w", 85)),
                                            height = tools.adapt_dimensions(app, "h", 25)), 
                                        bgcolor=app.theme.additional_color, border_radius = 10, width = tools.adapt_dimensions(app, "w", 92), height = tools.adapt_dimensions(app, "h", 40))
    
    welcome_icon, welcome_msg = utils.welcome_message(main.player.user)
    app.add_element(app.alignment("cstart", 
                                app.alignment("rstart", 
                                    ft.Icon(welcome_icon, color=app.theme.primary, size=tools.adapt_dimensions(app, "w", 5)), 
                                    ft.Text(welcome_msg, style = tools.primary_text_style(app, 40, weight=ft.FontWeight.BOLD))), 
                                player_card,
                                ft.Button(
                                    content=app.alignment("ccenter",
                                        ft.Icon(utils.icon("tasks"), color=app.theme.secondary, size=tools.adapt_dimensions(app, "w", 15)),
                                        ft.Text("Proceed to tasks", style=tools.secondary_text_style(app, 40, weight=ft.FontWeight.BOLD))),
                                    style=tools.main_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
                                    width=tools.adapt_dimensions(app, "w", 92),
                                    height=tools.adapt_dimensions(app, "w", 25),
                                    on_click = to_tasks         
                                ),
                                *active_goals(app),
                                ft.Button(
                                    content=app.alignment("ccenter",
                                        ft.Icon(utils.icon("goals"), color=app.theme.secondary, size=tools.adapt_dimensions(app, "w", 15)),
                                        ft.Text("Goals configuration", style=tools.secondary_text_style(app, 40, weight=ft.FontWeight.BOLD))),
                                    style=tools.additional_button_style(app, 32, shape=ft.RoundedRectangleBorder(radius=10)),
                                    width=tools.adapt_dimensions(app, "w", 92),
                                    height=tools.adapt_dimensions(app, "w", 25),
                                    on_click = lambda: app.navigate("goals_configuration_page")       
                                ),                                
                                width = tools.adapt_dimensions(app, "w", 100), spacing = tools.adapt_dimensions(app, "w", 4), expand = True))


    
def build():
    app = App()

    app.set_size("1/4")
    app.set_version(info.VERSION)
    app.set_orientation("portrait")

    app.add_saved_keys("reg_data", "registered", "registered_version", "statistics", "daily_goals", "weekly_goals", "custom_goals", "active_goals", "gained_achievements")
    app.allow_delete_saved()

    app.add_page("loading_page", loading_ui)
    app.add_page("main_page", main_ui)
    app.add_page("tasks_navigation_page", tasks_navigation_ui)
    app.add_page("task_page", task_page)
    app.add_page("completement_page", completement_page)
    app.add_page("goals_configuration_page", goals_config_page)
    app.add_page("goal_page", goal_page)
    app.add_page("register_1", register_page_1_ui)
    app.add_page("register_2", register_page_2_ui)
    app.add_page("register_3", register_page_3_ui)

    app.add_top_button(
        icon = utils.icon("achievements"), 
        dialog_window = achievements_dialog, 
        tooltip = "Achievements", 
        icon_color=lambda theme: theme.cancel_button,
        pages=["main_page"]  
    )

    app.set_async_next(main.start)
    app.run(info.APP_NAME)