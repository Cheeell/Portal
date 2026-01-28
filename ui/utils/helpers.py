import os

def ensure_directory_exists(directory):
    """Ensure a directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename):
    """Sanitize filename to remove invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename_members(chat_name, all_users, dialog_id):
    """Save selected members to chat"""
    selected_members = [app_state.current_user]

    for user in all_users:
        if user != app_state.current_user:
            checkbox_tag = f"member_check_{user}"
            if dpg.does_item_exist(checkbox_tag) and dpg.get_value(checkbox_tag):
                selected_members.append(user)

    if chat_name in app_state.chat_settings:
        app_state.chat_settings[chat_name]["members"] = selected_members

    dpg.set_value("member_save_msg", "✓ Members updated successfully!")
    dpg.configure_item("member_save_msg", color=(0, 255, 0))

def send_message(node_id, chat_name, dialog_id):
    """Send message and update chat"""
    message = dpg.get_value(f"input_{node_id}")
    if message.strip():
        write_message(chat_name, message)
        dpg.set_value(f"input_{node_id}", "")
        refresh_chat(node_id, chat_name)

def refresh_chat(node_id, chat_name):
    """Refresh chat history display"""
    chat_content = read_chat(chat_name)
    if dpg.does_item_exist(f"history_{node_id}"):
        dpg.set_value(f"history_{node_id}", chat_content)

def show_create_chat_dialog():
    """Show dialog to create new chat"""
    dialog_id = "create_chat_dialog"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="Create New Chat", tag=dialog_id, modal=True,
                    width=400, height=250, pos=[250, 150]):
        dpg.add_text("Enter chat details:")
        dpg.add_separator()

        dpg.add_text("Chat Name:")
        dpg.add_input_text(tag="dialog_chat_name", width=350)

        dpg.add_separator()
        dpg.add_checkbox(label="🔒 Read-only (only you can write)",
                        tag="dialog_read_only", default_value=False)
        dpg.add_checkbox(label="👥 Group Chat (invite-only)",
                        tag="dialog_is_group", default_value=False)

        dpg.add_separator()
        dpg.add_text("", tag="dialog_create_message")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create", width=150,
                         callback=create_chat_from_dialog)
            dpg.add_button(label="Cancel", width=150,
                         callback=lambda: dpg.delete_item(dialog_id))

def create_chat_from_dialog():
    """Create chat from dialog inputs"""
    from chat.chat_nodes import create_chat_node

    chat_name = dpg.get_value("dialog_chat_name")

    if not chat_name or not chat_name.strip():
        dpg.set_value("dialog_create_message", "Please enter a chat name!")
        dpg.configure_item("dialog_create_message", color=(255, 0, 0))
        return

    chat_name = chat_name.strip()
    read_only = dpg.get_value("dialog_read_only")
    is_group = dpg.get_value("dialog_is_group")

    create_chat_node(chat_name, read_only, is_group)
    dpg.delete_item("create_chat_dialog")
