# ===========================================
# FILE: auth/ui.py
# ===========================================
import dearpygui.dearpygui as dpg
from auth.user_manager import (
    login_user, register_user, get_user_color,
    save_last_login, get_last_login,
    create_session, check_session, clear_session, get_session_info
)
from config import app_state


def show_login_screen(on_success_callback):
    """Show login/register screen or auto-login if session exists"""

    # Check for existing valid session
    session_username = check_session()
    if session_username:
        # Auto-login with existing session
        print(f"Auto-login with session: {session_username}")
        app_state.current_user = session_username
        app_state.current_user_color = get_user_color(session_username)
        on_success_callback()
        return

    # No valid session, show login screen
    last_user = get_last_login()

    with dpg.window(label="Login", tag="login_window", width=450, height=520,
                    pos=[200, 100], no_close=True, no_collapse=True):
        dpg.add_text("Welcome to Messenger")
        dpg.add_separator()

        dpg.add_text("Username:")
        dpg.add_input_text(tag="login_username", width=350, default_value=last_user)

        dpg.add_text("Password:")
        dpg.add_input_text(tag="login_password", width=350, password=True,
                           on_enter=True, callback=lambda: attempt_login(on_success_callback))

        if last_user:
            dpg.add_text(f"💡 Last login: {last_user}", color=(150, 200, 255))

        dpg.add_separator()

        # Remember Me checkbox
        dpg.add_checkbox(label="🔐 Remember me for 14 days (auto-login)",
                         tag="remember_me_checkbox",
                         default_value=False)
        dpg.add_text("Keep me logged in on this device",
                     color=(150, 150, 150), wrap=350)

        dpg.add_separator()
        dpg.add_text("Choose Your Color (for registration):", color=(200, 200, 255))

        dpg.add_color_edit(tag="user_color_picker",
                           default_value=[100, 150, 255, 255],
                           no_alpha=True,
                           width=350)

        with dpg.group(horizontal=True):
            dpg.add_text("Color preview: ")
            dpg.add_text("Your Username", tag="color_preview", color=[100, 150, 255])

        dpg.set_item_callback("user_color_picker", update_color_preview)

        dpg.add_separator()
        dpg.add_text("", tag="login_message", color=(255, 0, 0))

        with dpg.group(horizontal=True):
            dpg.add_button(label="Login", width=165,
                           callback=lambda: attempt_login(on_success_callback))
            dpg.add_button(label="Register", width=165, callback=attempt_register)


def update_color_preview(sender, app_data):
    """Update the color preview text when color picker changes"""
    if isinstance(app_data, (list, tuple)) and len(app_data) >= 3:
        if all(0.0 <= val <= 1.0 for val in app_data[:3]):
            rgb_color = [int(app_data[i] * 255) for i in range(3)]
        else:
            rgb_color = [int(app_data[i]) for i in range(3)]
    else:
        return

    if dpg.does_item_exist("color_preview"):
        dpg.configure_item("color_preview", color=rgb_color)


def attempt_login(on_success_callback):
    """Handle login attempt"""
    username = dpg.get_value("login_username")
    password = dpg.get_value("login_password")
    remember_me = dpg.get_value("remember_me_checkbox")

    if not username or not password:
        dpg.set_value("login_message", "Please enter username and password")
        return

    success, message = login_user(username, password)

    if success:
        app_state.current_user = username
        app_state.current_user_color = get_user_color(username)

        # Save last login
        save_last_login(username)

        # Create session if remember me is checked
        if remember_me:
            create_session(username, remember_me=True)
            print(f"✓ Session created - you'll stay logged in for 14 days")
        else:
            # Make sure no old session exists
            clear_session()

        dpg.delete_item("login_window")
        on_success_callback()
    else:
        dpg.set_value("login_message", message)


def attempt_register():
    """Handle registration attempt"""
    username = dpg.get_value("login_username")
    password = dpg.get_value("login_password")
    color_rgba = dpg.get_value("user_color_picker")

    if all(0.0 <= val <= 1.0 for val in color_rgba[:3]):
        color = [int(color_rgba[i] * 255) for i in range(3)]
    else: #елс стамент
        color = [int(color_rgba[i]) for i in range(3)]

    if not username or not password:
        dpg.set_value("login_message", "Please enter username and password")
        return

    if len(password) < 4:
        dpg.set_value("login_message", "Password must be at least 4 characters")
        return

    success, message = register_user(username, password, color)
    dpg.set_value("login_message", message)

    if success:
        dpg.configure_item("login_message", color=(0, 255, 0))
    else:
        dpg.configure_item("login_message", color=(255, 0, 0))