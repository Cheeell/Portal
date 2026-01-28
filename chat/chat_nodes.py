# ===========================================
# FILE: chat/chat_nodes.py
# ===========================================

import dearpygui.dearpygui as dpg
import random
from chat.chat_manager import create_chat
from chat.ui import show_chat_dialog, show_member_management
from config import app_state


def create_chat_node(chat_name, read_only=False, is_group=False):
    """Create a new chat node"""

    # VALIDATION: Check if node editor exists
    if not app_state.node_editor:
        print("ERROR: node_editor is None! Cannot create chat node.")
        return None

    if not dpg.does_item_exist(app_state.node_editor):
        print(f"ERROR: node_editor {app_state.node_editor} doesn't exist!")
        return None

    print(f"Creating chat node: {chat_name}")  # DEBUG

    chat_settings = create_chat(chat_name, read_only, is_group)

    new_node_id = dpg.generate_uuid()
    app_state.node_chats[new_node_id] = chat_name

    label = ""
    if is_group:
        label += "👥 "
    if read_only:
        label += "🔒 "
    label += chat_name

    pos = [random.randint(50, 400), random.randint(50, 300)]

    with dpg.node(label=label, pos=pos, parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            icon = "👥" if is_group else "💬"

            with dpg.group(horizontal=True):
                dpg.add_text(f"{icon} {chat_name}")
                dpg.add_button(label="❌", width=30,
                               callback=lambda: delete_chat_node(new_node_id, chat_name))

            if read_only:
                dpg.add_text(f"🔒 Author: {app_state.current_user}",
                             color=app_state.current_user_color)
            if is_group:
                members = chat_settings.get("members", [])
                dpg.add_text(f"Members: {len(members)}", color=(150, 200, 255))

            dpg.add_button(label="Open Chat", callback=show_chat_dialog, user_data=new_node_id)

    if is_group:
        show_member_management(chat_name, None)

    print(f"Successfully created chat node: {chat_name} with ID: {new_node_id}")  # DEBUG
    return new_node_id


def delete_chat_node(node_id, chat_name):
    """Delete a chat node"""
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    if node_id in app_state.node_chats:
        del app_state.node_chats[node_id]