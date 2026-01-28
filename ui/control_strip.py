# ===========================================
# FILE: ui/control_strip.py (COMPLETE)
# ===========================================
import dearpygui.dearpygui as dpg
from config import app_state

def on_add_file():
    """Handle adding a file"""
    print("Add File clicked")
    from nodes.file import show_add_file_dialog
    close_add_menu()
    show_add_file_dialog()

# Add this callback:
def show_saved_messages_dialog_callback():
    from chat.saved_messages import show_saved_messages_dialog
    show_saved_messages_dialog()


def create_control_strip():
    """Create the bottom control strip with consolidated Add menu"""
    viewport_width = dpg.get_viewport_width()
    viewport_height = dpg.get_viewport_height()
    strip_height = 40

    with dpg.window(label="Control Strip", tag="control_strip",
                    pos=(0, viewport_height - strip_height),
                    width=viewport_width,
                    height=strip_height,
                    no_title_bar=True, no_move=True, no_resize=True,
                    no_collapse=True, no_close=True):
        from ui.dialogs import show_settings, show_about, logout

        # Left side buttons
        with dpg.group(horizontal=True, pos=(10, 5)):
            dpg.add_button(label="Add", callback=show_add_menu,
                           width=70, height=30, tag="add_menu_button")
            dpg.add_spacer(width=10)
            dpg.add_button(label="Settings", callback=show_settings,
                           width=80, height=30)
            dpg.add_button(label="About", callback=show_about,
                           width=70, height=30)
            # In create_control_strip() function, add this button:
            dpg.add_button(label="Saved", callback=show_saved_messages_dialog_callback,
                           width=80, height=30)



        # Right side username and logout
        logout_width = 70
        spacing = 20
        initial_right_pos = viewport_width / 2

        with dpg.group(horizontal=True, tag="right_group", pos=(initial_right_pos, 10)):
            dpg.add_text("User: ", color=(200, 200, 200))
            dpg.add_text(app_state.current_user, tag="main_user_display",
                         color=app_state.current_user_color)
            dpg.add_spacer(width=spacing)
            dpg.add_button(label="Logout", callback=logout, width=logout_width, height=30)


def show_add_menu():
    """Show popup menu with all add options"""
    menu_id = "add_popup_menu"

    # Delete existing menu if it exists
    if dpg.does_item_exist(menu_id):
        dpg.delete_item(menu_id)

    # Get button position to place menu nearby
    button_pos = dpg.get_item_pos("add_menu_button")
    viewport_height = dpg.get_viewport_height()

    # Position menu above the button
    menu_x = button_pos[0]
    menu_y = viewport_height - 340  # Increased height for audio button

    with dpg.window(label="Add New Item", tag=menu_id,
                    pos=[menu_x, menu_y],
                    width=200,
                    height=305,  # Increased height
                    no_move=False,
                    no_resize=True,
                    no_collapse=True,
                    modal=False,
                    on_close=lambda: close_add_menu()):
        dpg.add_text("Select item to add:", color=(100, 200, 255))
        dpg.add_separator()

        # Add buttons for each type with proper callbacks
        dpg.add_button(label="Chat",
                       callback=on_add_chat,
                       width=180, height=30)

        dpg.add_button(label="Python Script",
                       callback=on_add_script,
                       width=180, height=30)

        dpg.add_button(label="Highlight Box",
                       callback=on_add_highlight,
                       width=180, height=30)

        dpg.add_button(label="Text Note",
                       callback=on_add_text,
                       width=180, height=30)

        dpg.add_button(label="Image",
                       callback=on_add_image,
                       width=180, height=30)

        dpg.add_button(label="Audio",
                       callback=on_add_audio,
                       width=180, height=30)
        dpg.add_button(label="File",
                       callback=on_add_file,
                       width=180, height=30)

        dpg.add_separator()
        dpg.add_button(label="Cancel",
                       callback=close_add_menu,
                       width=180, height=25)



def close_add_menu():
    """Close the add menu"""
    menu_id = "add_popup_menu"
    if dpg.does_item_exist(menu_id):
        dpg.delete_item(menu_id)


def on_add_chat():
    """Handle adding a chat"""
    print("Add Chat clicked")
    from chat.ui import show_create_chat_dialog
    close_add_menu()
    show_create_chat_dialog()


def on_add_script():
    """Handle adding a script"""
    print("Add Script clicked")
    from scripts.ui import show_script_editor
    close_add_menu()
    show_script_editor()


def on_add_highlight():
    """Handle adding a highlight box"""
    print("Add Highlight clicked")
    from nodes.highlight import show_create_highlight_dialog
    close_add_menu()
    show_create_highlight_dialog()


def on_add_text():
    """Handle adding a text note"""
    print("Add Text clicked")
    from nodes.text import show_create_text_dialog
    close_add_menu()
    show_create_text_dialog()


def on_add_image():
    """Handle adding an image"""
    print("Add Image clicked")
    from nodes.image import show_add_image_dialog
    close_add_menu()
    show_add_image_dialog()


def on_add_audio():
    """Handle adding an audio file"""
    print("Add Audio clicked")
    from nodes.audio import show_add_audio_dialog
    close_add_menu()
    show_add_audio_dialog()


def update_control_strip_position():
    """Update control strip position and size when viewport changes"""
    if dpg.does_item_exist("control_strip"):
        viewport_width = dpg.get_viewport_width()
        viewport_height = dpg.get_viewport_height()
        strip_height = 40

        dpg.configure_item("control_strip",
                           pos=(0, viewport_height - strip_height),
                           width=viewport_width)