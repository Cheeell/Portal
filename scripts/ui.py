
import dearpygui.dearpygui as dpg
from scripts.script_manager import save_script, load_script
from scripts.script_nodes import add_script_node
from config import app_state

def show_script_editor(script_name=None):
    """Show script editor in main window"""
    if dpg.does_item_exist("node_editor_container"):
        dpg.hide_item("node_editor_container")

    if dpg.does_item_exist("script_editor_container"):
        dpg.delete_item("script_editor_container")

    script_content = ""
    if script_name:
        script_content = load_script(script_name)

    with dpg.group(tag="script_editor_container", parent="messenger_window"):
        dpg.add_text("📝 Script Editor", color=(100, 255, 100))
        dpg.add_separator()

        dpg.add_text("Script Name:")
        dpg.add_input_text(tag="script_name_input", width=300,
                          default_value=script_name if script_name else "")

        dpg.add_separator()
        dpg.add_text("Python Code:")
        dpg.add_input_text(tag="script_code_input", default_value=script_content,
                          multiline=True, width=780, height=350, tab_input=True)

        dpg.add_separator()
        dpg.add_text("", tag="script_save_message")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Script", width=120, callback=save_script_from_editor)
            dpg.add_button(label="Back to Messenger", width=150, callback=close_script_editor)

def close_script_editor():
    """Close script editor and return to messenger"""
    if dpg.does_item_exist("script_editor_container"):
        dpg.delete_item("script_editor_container")

    if dpg.does_item_exist("node_editor_container"):
        dpg.show_item("node_editor_container")

def save_script_from_editor():
    """Save Python script from editor"""
    script_name = dpg.get_value("script_name_input").strip()
    script_code = dpg.get_value("script_code_input")

    if not script_name:
        dpg.set_value("script_save_message", "Please enter a script name!")
        dpg.configure_item("script_save_message", color=(255, 0, 0))
        return

    save_script(script_name, script_code)

    dpg.set_value("script_save_message", f"Script '{script_name}.py' saved successfully!")
    dpg.configure_item("script_save_message", color=(0, 255, 0))

    add_script_node(script_name)
    close_script_editor()
