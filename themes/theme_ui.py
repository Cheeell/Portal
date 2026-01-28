# ===========================================
# FILE: themes/theme_ui.py
# ===========================================
import dearpygui.dearpygui as dpg
from themes.theme_manager import (
    get_all_themes, apply_theme, create_custom_theme,
    update_custom_theme, delete_custom_theme, is_custom_theme,
    load_theme_preference
)


def show_theme_settings():
    """Show theme settings window"""
    dialog_id = "theme_settings_window"

    # Force delete if exists
    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    current_theme = load_theme_preference()
    all_themes = get_all_themes()

    with dpg.window(label="Theme Settings", tag=dialog_id, modal=False,
                    width=700, height=600, pos=[100, 50], show=True):

        dpg.add_text("🎨 Choose Your Theme", color=(100, 200, 255))
        dpg.add_separator()

        # Theme selection
        dpg.add_text("Select Theme:")
        theme_names = list(all_themes.keys())

        dpg.add_combo(
            items=theme_names,
            tag="theme_selector",
            default_value=current_theme,
            width=400,
            callback=preview_theme
        )

        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply Theme", width=120, callback=apply_selected_theme)
            dpg.add_button(label="Preview", width=80, callback=preview_theme)

        dpg.add_separator()

        # Custom theme creation
        dpg.add_text("📝 Create Custom Theme", color=(150, 255, 150))
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_text("New Theme Name:")
            dpg.add_input_text(tag="new_theme_name", width=200, hint="My Custom Theme")

        with dpg.group(horizontal=True):
            dpg.add_text("Base Theme:")
            dpg.add_combo(
                items=theme_names,
                tag="base_theme_selector",
                default_value="Dark (Default)",
                width=200
            )

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create Custom Theme", width=150,
                           callback=create_new_custom_theme)
            dpg.add_button(label="Edit Selected Theme", width=150,
                           callback=edit_selected_theme)

        dpg.add_text("", tag="theme_create_message")

        dpg.add_separator()

        # Theme management
        dpg.add_text("🗑️ Manage Custom Themes", color=(255, 150, 150))
        dpg.add_separator()

        selected_theme = dpg.get_value("theme_selector")
        if is_custom_theme(selected_theme):
            dpg.add_text(f"Selected: {selected_theme} (Custom)", color=(255, 200, 100))
            dpg.add_button(label="Delete This Custom Theme", width=200,
                           callback=lambda: delete_selected_theme(selected_theme))
        else:
            dpg.add_text("Select a custom theme to delete it", color=(150, 150, 150))

        dpg.add_separator()

        # Preview colors
        dpg.add_text("Theme Preview:", color=(200, 200, 100))
        with dpg.group(horizontal=True):
            dpg.add_button(label="Button", width=80)
            dpg.add_checkbox(label="Checkbox")
            dpg.add_input_text(hint="Input", width=100)

        dpg.add_separator()
        dpg.add_button(label="Close", width=150, callback=lambda: dpg.delete_item(dialog_id))

    # Force focus on the window
    dpg.focus_item(dialog_id)
    print(f"Theme settings window created with ID: {dialog_id}")


def preview_theme(sender=None, app_data=None):
    """Preview selected theme without saving"""
    theme_name = dpg.get_value("theme_selector")
    apply_theme(theme_name)


def apply_selected_theme():
    """Apply and save selected theme"""
    theme_name = dpg.get_value("theme_selector")
    apply_theme(theme_name)

    if dpg.does_item_exist("theme_create_message"):
        dpg.set_value("theme_create_message", f"✓ Theme '{theme_name}' applied!")
        dpg.configure_item("theme_create_message", color=(0, 255, 0))


def create_new_custom_theme():
    """Create a new custom theme"""
    theme_name = dpg.get_value("new_theme_name").strip()
    base_theme = dpg.get_value("base_theme_selector")

    if not theme_name:
        dpg.set_value("theme_create_message", "Please enter a theme name!")
        dpg.configure_item("theme_create_message", color=(255, 0, 0))
        return

    if theme_name in get_all_themes():
        dpg.set_value("theme_create_message", "Theme name already exists!")
        dpg.configure_item("theme_create_message", color=(255, 0, 0))
        return

    create_custom_theme(theme_name, base_theme)

    # Update theme selector
    all_themes = get_all_themes()
    dpg.configure_item("theme_selector", items=list(all_themes.keys()))
    dpg.set_value("theme_selector", theme_name)

    dpg.set_value("theme_create_message", f"✓ Custom theme '{theme_name}' created!")
    dpg.configure_item("theme_create_message", color=(0, 255, 0))

    # Clear input
    dpg.set_value("new_theme_name", "")


def edit_selected_theme():
    """Open theme editor for selected theme"""
    theme_name = dpg.get_value("theme_selector")

    if not is_custom_theme(theme_name):
        dpg.set_value("theme_create_message", "Cannot edit standard themes! Create a custom theme first.")
        dpg.configure_item("theme_create_message", color=(255, 150, 0))
        return

    show_theme_editor(theme_name)


def delete_selected_theme(theme_name):
    """Delete a custom theme"""
    if delete_custom_theme(theme_name):
        # Update theme selector
        all_themes = get_all_themes()
        dpg.configure_item("theme_selector", items=list(all_themes.keys()))
        dpg.set_value("theme_selector", "Dark (Default)")

        dpg.set_value("theme_create_message", f"✓ Theme '{theme_name}' deleted!")
        dpg.configure_item("theme_create_message", color=(0, 255, 0))

        # Refresh the window
        show_theme_settings()


def show_theme_editor(theme_name):
    """Show detailed theme editor for a custom theme"""
    editor_id = "theme_editor_window"

    if dpg.does_item_exist(editor_id):
        dpg.delete_item(editor_id)

    all_themes = get_all_themes()
    theme_data = all_themes[theme_name]

    with dpg.window(label=f"Edit Theme: {theme_name}", tag=editor_id, modal=False,
                    width=600, height=700, pos=[150, 50], show=True):

        dpg.add_text(f"Editing: {theme_name}", color=(100, 255, 200))
        dpg.add_separator()

        dpg.add_text("💡 Tip: Changes are saved automatically", color=(150, 150, 150))
        dpg.add_separator()

        # Create color pickers for each theme element
        color_categories = {
            "Windows & Backgrounds": ["WindowBg", "ChildBg", "PopupBg", "MenuBarBg"],
            "Borders & Frames": ["Border", "FrameBg", "FrameBgHovered", "FrameBgActive"],
            "Title Bars": ["TitleBg", "TitleBgActive"],
            "Scrollbars": ["ScrollbarBg", "ScrollbarGrab"],
            "Buttons": ["Button", "ButtonHovered", "ButtonActive", "CheckMark"],
            "Headers & Tabs": ["Header", "HeaderHovered", "HeaderActive", "Tab", "TabHovered", "TabActive"],
            "Sliders": ["SliderGrab"],
            "Text": ["Text", "TextDisabled"],
        }

        for category, color_names in color_categories.items():
            with dpg.collapsing_header(label=category, default_open=False):
                for color_name in color_names:
                    if color_name in theme_data:
                        color_value = theme_data[color_name]

                        with dpg.group(horizontal=True):
                            dpg.add_text(f"{color_name}:", width=150)
                            dpg.add_color_edit(
                                tag=f"color_{theme_name}_{color_name}",
                                default_value=color_value,
                                width=200,
                                alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                                callback=lambda s, a, u: update_theme_color(u[0], u[1], a),
                                user_data=(theme_name, color_name)
                            )

        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply & Preview", width=130,
                           callback=lambda: apply_theme(theme_name))
            dpg.add_button(label="Close", width=130,
                           callback=lambda: dpg.delete_item(editor_id))

    dpg.focus_item(editor_id)


def update_theme_color(theme_name, color_name, color_value):
    """Update a color in the theme"""
    update_custom_theme(theme_name, color_name, color_value)

    # Auto-preview
    apply_theme(theme_name)