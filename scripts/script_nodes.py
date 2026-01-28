# ===========================================
# FILE: scripts/script_nodes.py
# ===========================================
import dearpygui.dearpygui as dpg
import random
from scripts.script_manager import run_script, stop_script
from config import app_state


def add_script_node(script_name):
    """Add script node to messenger"""

    # VALIDATION: Check if node editor exists
    if not app_state.node_editor:
        print("ERROR: node_editor is None! Cannot create script node.")
        return None

    if not dpg.does_item_exist(app_state.node_editor):
        print(f"ERROR: node_editor {app_state.node_editor} doesn't exist!")
        return None

    if script_name in app_state.script_nodes:
        print(f"Script node {script_name} already exists")
        return app_state.script_nodes[script_name]

    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()
    app_state.script_nodes[script_name] = new_node_id

    with dpg.node(label=f"🐍 {script_name}", pos=pos,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.group(horizontal=True):
                dpg.add_text(f"📜 {script_name}.py", color=(100, 255, 100))
                dpg.add_button(label="❌", width=30,
                               callback=lambda: delete_script_node(new_node_id, script_name))

            dpg.add_text(f"By: {app_state.current_user}", color=app_state.current_user_color)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Run", width=70,
                               callback=lambda: run_script(script_name))
                dpg.add_button(label="Edit", width=70,
                               callback=lambda sn=script_name: edit_script_callback(sn))
                dpg.add_button(label="Stop", width=70,
                               callback=lambda: stop_script(script_name))

    print(f"Successfully created script node: {script_name}")
    return new_node_id


def edit_script_callback(script_name):
    """Callback for edit button - imports show_script_editor lazily"""
    from scripts.ui import show_script_editor
    show_script_editor(script_name)


def delete_script_node(node_id, script_name):
    """Delete a script node"""
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    if script_name in app_state.script_nodes:
        del app_state.script_nodes[script_name]

    if script_name in app_state.running_processes:
        stop_script(script_name)