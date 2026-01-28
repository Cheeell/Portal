# ===========================================
# FILE: chat/saved_messages.py (NEW FILE)
# ===========================================

import dearpygui.dearpygui as dpg
import os
from datetime import datetime
from config import app_state, CHATS_DIR

SAVED_MESSAGES_DIR = "saved_messages"
if not os.path.exists(SAVED_MESSAGES_DIR):
    os.makedirs(SAVED_MESSAGES_DIR)


def get_saved_messages_file():
    """Get the saved messages file for current user"""
    return os.path.join(SAVED_MESSAGES_DIR, f"{app_state.current_user}_saved.txt")


def save_message_to_saved(message_text, original_chat=None, original_author=None):
    """Save a message to saved messages"""
    filepath = get_saved_messages_file()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format: [timestamp] From: chat_name | author: message
    if original_chat and original_author:
        formatted = f"[{timestamp}] From: {original_chat} | {original_author}: {message_text}\n"
    else:
        formatted = f"[{timestamp}] {app_state.current_user}: {message_text}\n"

    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(formatted)

    print(f"✓ Message saved to Saved Messages")


def read_saved_messages():
    """Read all saved messages for current user"""
    filepath = get_saved_messages_file()

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


def show_saved_messages_dialog():
    """Show saved messages dialog (like Telegram's Saved Messages)"""
    dialog_id = "saved_messages_dialog"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="💾 Saved Messages", tag=dialog_id,
                    modal=False, width=600, height=550, pos=[100, 100]):
        with dpg.group(horizontal=True):
            dpg.add_text("💾 Your Saved Messages", color=(100, 255, 200))
            dpg.add_button(label="🗑️ Clear All", width=100,
                           callback=confirm_clear_saved_messages)

        dpg.add_separator()
        dpg.add_text("Messages you've saved from any chat", color=(150, 150, 150))
        dpg.add_separator()

        # Scrollable area for saved messages
        with dpg.child_window(tag=f"saved_scroll", width=-1, height=300, border=True):
            display_saved_messages()

        dpg.add_separator()

        # New message section
        dpg.add_text("📝 Add New Message:", color=(150, 200, 255))
        dpg.add_input_text(tag="saved_new_message", multiline=True,
                           width=-1, height=80,
                           hint="Type a message to save...")

        with dpg.group(horizontal=True):
            dpg.add_button(label="💾 Save", width=120,
                           callback=save_new_message_callback)
            dpg.add_button(label="🔄 Refresh", width=80,
                           callback=refresh_saved_messages)
            dpg.add_button(label="Close", width=80,
                           callback=lambda: dpg.delete_item(dialog_id))


def display_saved_messages():
    """Display all saved messages with formatting"""
    content = read_saved_messages()
    scroll_id = "saved_scroll"

    if not content.strip():
        dpg.add_text("No saved messages yet...",
                     color=(150, 150, 150), parent=scroll_id)
        dpg.add_text("💡 Save messages from any chat by right-clicking them",
                     color=(100, 150, 200), parent=scroll_id, wrap=550)
        return

    lines = content.strip().split('\n')

    for line in lines:
        if not line.strip():
            continue

        # Parse the line
        # Format: [timestamp] From: chat | author: message
        # or: [timestamp] user: message

        try:
            # Extract timestamp
            if line.startswith('['):
                timestamp_end = line.index(']')
                timestamp = line[1:timestamp_end]
                rest = line[timestamp_end + 2:]  # Skip '] '

                # Check if it has "From:" prefix
                if rest.startswith("From: "):
                    rest = rest[6:]  # Remove "From: "

                    if ' | ' in rest:
                        chat_and_author, message = rest.split(':', 1)
                        chat_name, author = chat_and_author.split(' | ')

                        # Display with formatting
                        with dpg.group(parent=scroll_id, horizontal=False):
                            with dpg.group(horizontal=True):
                                dpg.add_text(f"[{timestamp}]", color=(100, 150, 200))
                                dpg.add_text(f"From: {chat_name}", color=(255, 200, 100))

                            with dpg.group(horizontal=True):
                                dpg.add_text(f"{author}:", color=(150, 255, 150))
                                dpg.add_text(message.strip(), wrap=500)

                            dpg.add_spacer(height=5)
                    else:
                        # Fallback format
                        dpg.add_text(line, parent=scroll_id, wrap=550)
                        dpg.add_spacer(height=5, parent=scroll_id)
                else:
                    # Simple format: [timestamp] user: message
                    with dpg.group(parent=scroll_id, horizontal=False):
                        dpg.add_text(f"[{timestamp}]", color=(100, 150, 200))
                        dpg.add_text(rest, wrap=520)
                        dpg.add_spacer(height=5)
            else:
                dpg.add_text(line, parent=scroll_id, wrap=550)
                dpg.add_spacer(height=5, parent=scroll_id)

        except Exception as e:
            # Fallback if parsing fails
            dpg.add_text(line, parent=scroll_id, wrap=550, color=(200, 200, 200))
            dpg.add_spacer(height=5, parent=scroll_id)


def refresh_saved_messages():
    """Refresh the saved messages display"""
    if dpg.does_item_exist("saved_scroll"):
        dpg.delete_item("saved_scroll", children_only=True)
        display_saved_messages()


def save_new_message_callback():
    """Save a new message from the input field"""
    message = dpg.get_value("saved_new_message")

    if message and message.strip():
        save_message_to_saved(message.strip())
        dpg.set_value("saved_new_message", "")
        refresh_saved_messages()


def confirm_clear_saved_messages():
    """Show confirmation dialog before clearing all saved messages"""
    confirm_id = "confirm_clear_saved"

    if dpg.does_item_exist(confirm_id):
        dpg.delete_item(confirm_id)

    with dpg.window(label="⚠️ Confirm Clear", tag=confirm_id, modal=True,
                    width=400, height=150, pos=[300, 250]):
        dpg.add_text("Are you sure you want to delete ALL saved messages?",
                     color=(255, 200, 100), wrap=380)
        dpg.add_text("This action cannot be undone!", color=(255, 100, 100))
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="🗑️ Delete All", width=150,
                           callback=lambda: [clear_all_saved_messages(),
                                             dpg.delete_item(confirm_id)])
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(confirm_id))


def clear_all_saved_messages():
    """Clear all saved messages for current user"""
    filepath = get_saved_messages_file()

    if os.path.exists(filepath):
        os.remove(filepath)

    refresh_saved_messages()
    print("✓ All saved messages cleared")


def add_save_button_to_chat(chat_dialog_id, chat_name):
    """Add a 'Save to Saved Messages' button to chat dialogs"""
    # This function can be called when creating chat dialogs
    # to add a button that saves the current message
    pass


# ===========================================
# INTEGRATION: Add to chat/ui.py
# ===========================================

def show_chat_dialog_with_save_button(sender, app_data, user_data):
    """
    Modified version of show_chat_dialog that includes save button

    Add this to chat/ui.py or modify existing show_chat_dialog
    """
    from chat.saved_messages import save_message_to_saved

    node_id = user_data
    chat_name = app_state.node_chats.get(node_id, "unknown")
    chat_settings = app_state.chat_settings.get(chat_name, {})

    # ... existing chat dialog code ...

    # Add "Save Message" button in the message input area
    # This would go after the message input field:

    """
    with dpg.group(horizontal=True):
        dpg.add_button(label="Send Message", width=120,
                      callback=lambda: send_message(node_id, chat_name, dialog_id))
        dpg.add_button(label="💾 Save to Saved", width=120,
                      callback=lambda: save_current_message_to_saved(
                          dpg.get_value(f"input_{node_id}"), 
                          chat_name, 
                          app_state.current_user))
        dpg.add_button(label="Refresh", width=80,
                      callback=lambda: refresh_chat_with_mentions(node_id, chat_name))
    """


def save_current_message_to_saved(message, chat_name, author):
    """Helper to save current message being typed"""
    from chat.saved_messages import save_message_to_saved

    if message and message.strip():
        save_message_to_saved(message.strip(), chat_name, author)
        # Optionally clear the input
        # dpg.set_value(f"input_{node_id}", "")