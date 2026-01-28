import os
from datetime import datetime
from config import CHATS_DIR, app_state

def read_chat(chat_name):
    """Read chat messages from .txt file"""
    filepath = os.path.join(CHATS_DIR, f"{chat_name}.txt")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def write_message(chat_name, message, username=None):
    """Append message to chat .txt file"""
    filepath = os.path.join(CHATS_DIR, f"{chat_name}.txt")
    timestamp = ""
    user = username if username else app_state.current_user
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f" {user}: {message}\n")

def create_chat(chat_name, read_only=False, is_group=False, members=None):
    """Create a new chat with settings"""
    if members is None:
        members = [app_state.current_user] if is_group else []

    app_state.chat_settings[chat_name] = {
        "author": app_state.current_user,
        "read_only": read_only,
        "is_group": is_group,
        "members": members
    }

    write_message(chat_name, f"Chat created by {app_state.current_user}", "System")
    if read_only:
        write_message(chat_name, "This is a read-only chat - only the author can write", "System")
    if is_group:
        write_message(chat_name, "This is a group chat - only invited members can join", "System")

    return app_state.chat_settings[chat_name]

def can_user_access_chat(chat_name):
    """Check if current user can access chat"""
    settings = app_state.chat_settings.get(chat_name, {})
    is_group = settings.get("is_group", False)
    members = settings.get("members", [])
    author = settings.get("author", "System")

    if not is_group:
        return True

    return app_state.current_user in members or app_state.current_user == author

def can_user_write_chat(chat_name):
    """Check if current user can write in chat"""
    settings = app_state.chat_settings.get(chat_name, {})
    read_only = settings.get("read_only", False)
    author = settings.get("author", "System")

    return not read_only or app_state.current_user == author