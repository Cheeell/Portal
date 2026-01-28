# ===========================================
# FILE: ui/messenger.py (UPDATED WITH DEBUG)
# ===========================================

import dearpygui.dearpygui as dpg
import os
from config import app_state, CHATS_DIR
from chat.chat_manager import write_message
from chat.chat_nodes import show_chat_dialog
from scripts.script_manager import load_all_scripts


def show_messenger():
    """Show main messenger interface"""
    print(f"\n=== show_messenger called ===")
    print(f"Current user: {app_state.current_user}")

    # Delete existing messenger window if it exists
    if dpg.does_item_exist("messenger_window"):
        print("Deleting existing messenger_window...")
        dpg.delete_item("messenger_window")

    try:
        with dpg.window(label=f"Messenger - {app_state.current_user}",
                        tag="messenger_window",
                        pos=(0, 0),
                        width=800,
                        height=560,
                        no_close=True):  # Prevent accidental closing

            print("Creating node editor...")
            app_state.node_editor = dpg.generate_uuid()
            print(f"Node editor ID: {app_state.node_editor}")

            with dpg.group(tag="node_editor_container"):
                with dpg.node_editor(tag=app_state.node_editor,
                                     minimap=True,
                                     minimap_location=dpg.mvNodeMiniMap_Location_BottomRight):
                    print("Creating initial chats...")
                    create_initial_chats()
                    print("✓ Initial chats created")

                    print("Loading scripts...")
                    load_all_scripts()
                    print("✓ Scripts loaded")

            # Load saved positions after creating nodes (delayed)
            dpg.set_frame_callback(5, load_positions_delayed)
            print("✓ Position loading scheduled")

        # Setup keyboard handler
        setup_keyboard_handler()
        print("✓ Keyboard handler set up")

        print(f"✓ Messenger window created successfully")

    except Exception as e:
        print(f"ERROR creating messenger window: {e}")
        import traceback
        traceback.print_exc()


def load_positions_delayed():
    """Load positions after a delay to ensure nodes are created"""
    try:
        from ui.node_position_manager import load_all_node_positions
        load_all_node_positions()
        print("✓ Node positions loaded")
    except Exception as e:
        print(f"Warning: Could not load positions: {e}")


def create_initial_chats():
    """Create initial example chats"""
    chats = [
        ("Help", [150, 150])
    ]

    for chat_name, pos in chats:
        print(f"Creating chat node: {chat_name}")
        chat_node = dpg.generate_uuid()
        app_state.node_chats[chat_node] = chat_name

        app_state.chat_settings[chat_name] = {
            "author": "System",
            "read_only": False,
            "is_group": False,
            "members": []
        }

        if not os.path.exists(os.path.join(CHATS_DIR, f"{chat_name}.txt")):
            write_message(chat_name, "Chat started", "System")

        try:
            with dpg.node(label=chat_name, pos=pos, tag=chat_node, parent=app_state.node_editor):
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    with dpg.group(horizontal=True):
                        dpg.add_text(f"💬 {chat_name}")
                        from chat.chat_nodes import delete_chat_node
                        dpg.add_button(label="❌", width=30,
                                       callback=lambda cn=chat_node, name=chat_name:
                                       delete_chat_node(cn, name))
                    dpg.add_button(label="Open Chat",
                                   callback=show_chat_dialog,
                                   user_data=chat_node)
            print(f"✓ Chat node '{chat_name}' created with ID: {chat_node}")
        except Exception as e:
            print(f"ERROR creating chat node '{chat_name}': {e}")


def setup_keyboard_handler():
    """Setup keyboard shortcuts"""
    with dpg.handler_registry():
        dpg.add_key_press_handler(callback=keyboard_handler)


def keyboard_handler(sender, app_data):
    """Handle keyboard shortcuts - Ctrl+X to delete selected nodes"""
    ctrl_pressed = dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl)

    if ctrl_pressed and app_data == 88:  # X key
        pass