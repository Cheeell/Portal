# ===========================================
# FILE: chat/ui.py (COMPLETE REDESIGNED VERSION)
# ===========================================

import dearpygui.dearpygui as dpg
from chat.chat_manager import read_chat, write_message, can_user_access_chat, can_user_write_chat
from chat.message_parser import format_message_for_display
from auth.user_manager import get_all_users, get_user_color
from config import app_state, CHATS_DIR
import re
import os
from datetime import datetime

# Store reply state
reply_state = {}


def show_chat_dialog(sender, app_data, user_data):
    """Modern chat dialog with Discord/Telegram-inspired design"""
    node_id = user_data
    chat_name = app_state.node_chats.get(node_id, "unknown")
    chat_settings = app_state.chat_settings.get(chat_name, {})
    chat_author = chat_settings.get("author", "System")
    read_only = chat_settings.get("read_only", False)
    members = chat_settings.get("members", [])
    is_group = chat_settings.get("is_group", False)

    # Check access
    if not can_user_access_chat(chat_name):
        show_access_denied_dialog(chat_name)
        return

    can_write = can_user_write_chat(chat_name)
    dialog_id = f"dialog_{node_id}"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    # Reset state
    reply_state[dialog_id] = None

    # Window styling
    with dpg.window(label="", tag=dialog_id,
                    modal=False, width=750, height=700, pos=[125, 50],
                    no_scrollbar=True):

        # === HEADER SECTION ===
        with dpg.group(tag=f"header_{dialog_id}"):
            with dpg.drawlist(width=730, height=70):
                # Gradient header background
                dpg.draw_rectangle((0, 0), (730, 70),
                                   fill=(35, 39, 45, 255),
                                   color=(50, 54, 60, 255), thickness=1)

                # Accent bar
                dpg.draw_rectangle((0, 0), (730, 3),
                                   fill=(88, 101, 242, 255))

                # Chat icon and title
                icon = "👥" if is_group else "💬"
                dpg.draw_circle((35, 35), 18,
                                fill=(88, 101, 242, 255), thickness=0)
                dpg.draw_text((27, 27), icon, size=20)

                dpg.draw_text((65, 20), chat_name,
                              color=(255, 255, 255, 255), size=18)

                # Status text
                if is_group:
                    status = f"{len(members)} members"
                elif read_only:
                    status = "🔒 Read-only"
                else:
                    status = "Private chat"

                dpg.draw_text((65, 45), status,
                              color=(185, 187, 190, 255), size=12)

                # Info button in header
                dpg.draw_circle((690, 35), 15,
                                fill=(54, 57, 63, 255), thickness=0)
                dpg.draw_text((683, 27), "ℹ", size=16, color=(185, 187, 190, 255))

            # Create clickable info button
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=675)
                dpg.add_button(label="ℹ", width=35, height=35,
                               callback=lambda: show_chat_info(chat_name, dialog_id))
                dpg.add_button(label="✕", width=35, height=35,
                               callback=lambda: dpg.delete_item(dialog_id))

        dpg.add_separator()

        # === MESSAGES AREA ===
        with dpg.child_window(tag=f"chat_scroll_{node_id}",
                              width=-1, height=480, border=False):
            display_enhanced_chat(node_id, chat_name, dialog_id)

        dpg.add_separator()

        # === INPUT AREA ===
        if can_write:
            # Reply preview bar (hidden by default)
            with dpg.group(tag=f"reply_bar_{dialog_id}", show=False):
                with dpg.drawlist(width=710, height=45):
                    dpg.draw_rectangle((0, 0), (710, 45),
                                       fill=(47, 49, 54, 255),
                                       color=(88, 101, 242, 100), thickness=2)
                    dpg.draw_line((0, 0), (5, 0),
                                  color=(88, 101, 242, 255), thickness=45)

                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=15)
                    with dpg.group():
                        dpg.add_spacer(height=5)
                        dpg.add_text("", tag=f"reply_to_{dialog_id}",
                                     color=(185, 187, 190, 255))
                        dpg.add_text("", tag=f"reply_preview_{dialog_id}",
                                     color=(220, 221, 222, 255), wrap=600)

                    dpg.add_button(label="✕", width=30, height=30,
                                   callback=lambda: cancel_reply(dialog_id))

                dpg.add_spacer(height=5)

            # Input box with enhanced styling
            with dpg.group():
                dpg.add_text("💬 Your message:", color=(185, 187, 190, 255))

                with dpg.child_window(border=True, height=110, width=-1):
                    dpg.add_input_text(tag=f"input_{node_id}",
                                       multiline=True,
                                       width=-1, height=75,
                                       hint="Type a message... (@mention users)")

                    # Mentions hint
                    all_users = get_all_users()
                    if all_users and len(all_users) > 0:
                        mentions = ", ".join([f"@{u}" for u in all_users[:6]])
                        if len(all_users) > 6:
                            mentions += "..."
                        dpg.add_text(f"💡 {mentions}",
                                     color=(114, 118, 125, 255), wrap=-1)

            dpg.add_spacer(height=5)

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="📤 Send", width=110, height=35,
                               callback=lambda: send_message(node_id, chat_name, dialog_id))

                dpg.add_spacer(width=5)
                dpg.add_button(label="🔄 Refresh", width=100, height=35,
                               callback=lambda: refresh_enhanced_chat(node_id, chat_name, dialog_id))

                # Formatting buttons
                dpg.add_spacer(width=20)
                dpg.add_button(label="😊", width=40, height=35,
                               callback=lambda: insert_text(node_id, "😊"))
                dpg.add_button(label="❤️", width=40, height=35,
                               callback=lambda: insert_text(node_id, "❤️"))
                dpg.add_button(label="👍", width=40, height=35,
                               callback=lambda: insert_text(node_id, "👍"))
                dpg.add_button(label="🎉", width=40, height=35,
                               callback=lambda: insert_text(node_id, "🎉"))

        else:
            # Read-only notice
            with dpg.drawlist(width=710, height=80):
                dpg.draw_rectangle((0, 0), (710, 80),
                                   fill=(64, 38, 38, 100),
                                   color=(220, 60, 60, 150), thickness=2)
                dpg.draw_text((30, 25), "🔒 This chat is read-only",
                              color=(255, 180, 180, 255), size=16)
                dpg.draw_text((30, 50), "Only the author can send messages",
                              color=(200, 150, 150, 255), size=12)

            with dpg.group(horizontal=True):
                dpg.add_spacer(width=300)
                dpg.add_button(label="🔄 Refresh", width=120, height=35,
                               callback=lambda: refresh_enhanced_chat(node_id, chat_name, dialog_id))


def display_enhanced_chat(node_id, chat_name, dialog_id):
    """Display chat messages with modern bubble design"""
    chat_content = read_chat(chat_name)
    scroll_window_id = f"chat_scroll_{node_id}"

    print(f"DEBUG: Displaying chat '{chat_name}' - content length: {len(chat_content)}")

    if not chat_content.strip():
        # Empty state
        with dpg.drawlist(width=700, height=400, parent=scroll_window_id):
            dpg.draw_rectangle((0, 0), (700, 400),
                               fill=(47, 49, 54, 255))

            # Empty state icon and text
            dpg.draw_circle((350, 170), 50,
                            fill=(88, 101, 242, 50),
                            color=(88, 101, 242, 100), thickness=3)
            dpg.draw_text((335, 160), "💬", size=40)

            dpg.draw_text((260, 240), "No messages yet",
                          color=(185, 187, 190, 255), size=18)
            dpg.draw_text((240, 270), "Start the conversation!",
                          color=(114, 118, 125, 255), size=14)
        return

    lines = chat_content.strip().split('\n')
    print(f"DEBUG: Processing {len(lines)} lines")

    # Group messages by day
    current_date = None

    for idx, line in enumerate(lines):
        if not line.strip():
            continue

        message_id = f"msg_{dialog_id}_{idx}"

        # Parse message - handle both formats
        pattern = r'\[(.*?)\] (.*?): (.*)'
        match = re.match(pattern, line)

        if not match:
            # Try simple format without timestamp
            simple_pattern = r'(.*?): (.*)'
            simple_match = re.match(simple_pattern, line.strip())
            if simple_match:
                username, message = simple_match.groups()
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"DEBUG: Parsed simple format - {username}: {message[:30]}")
            else:
                print(f"DEBUG: Failed to parse line {idx}: {line[:50]}")
                # Display as plain text
                with dpg.group(parent=scroll_window_id):
                    dpg.add_text(line, color=(150, 150, 150), wrap=680)
                    dpg.add_spacer(height=5)
                continue
        else:
            timestamp_str, username, message = match.groups()
            print(f"DEBUG: Parsed full format - [{timestamp_str}] {username}: {message[:30]}")

        # Parse timestamp
        try:
            msg_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            msg_date = msg_time.strftime("%B %d, %Y")
            msg_time_only = msg_time.strftime("%H:%M")
        except:
            msg_date = "Today"
            msg_time_only = timestamp_str.split()[-1] if ' ' in timestamp_str else timestamp_str

        # Date separator
        if msg_date != current_date:
            current_date = msg_date
            with dpg.group(parent=scroll_window_id):
                dpg.add_spacer(height=15)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=250)
                    with dpg.drawlist(width=200, height=25):
                        dpg.draw_rectangle((0, 8), (200, 17),
                                           fill=(54, 57, 63, 255),
                                           rounding=12)
                        dpg.draw_text((55, 5), msg_date,
                                      color=(185, 187, 190, 255), size=11)
                dpg.add_spacer(height=10)

        is_own = username == app_state.current_user
        user_color = get_user_color(username)

        # Message container
        with dpg.group(parent=scroll_window_id, horizontal=False):
            dpg.add_spacer(height=3)

            if is_own:
                # Own message (right-aligned)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=150)

                    # Message bubble with actions
                    create_message_bubble_with_actions(message_id, username, message, msg_time_only,
                                                       is_own, user_color, dialog_id,
                                                       chat_name, idx, line)
            else:
                # Other user's message (left-aligned)
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=10)

                    # Message bubble with actions
                    create_message_bubble_with_actions(message_id, username, message, msg_time_only,
                                                       is_own, user_color, dialog_id,
                                                       chat_name, idx, line)

            dpg.add_spacer(height=3)

    print(f"DEBUG: Finished displaying {len(lines)} messages")


def create_message_bubble_with_actions(msg_id, username, message, time, is_own,
                                       user_color, dialog_id, chat_name, idx, full_line):
    """Create a Windows XP-style message bubble with inline action buttons"""

    # Calculate bubble dimensions
    char_width = 7
    max_width = 450
    lines_in_msg = message.split('\n')
    longest_line = max(len(line) for line in lines_in_msg)

    bubble_width = min(max(longest_line * char_width + 40, 120), max_width)
    bubble_height = max(60, len(lines_in_msg) * 20 + 40)

    with dpg.group():
        # Username label (for others' messages)
        if not is_own:
            dpg.add_text(username, color=user_color, wrap=bubble_width - 20)
            dpg.add_spacer(height=2)

        # Message bubble with Windows XP styling
        with dpg.drawlist(width=bubble_width + 6, height=bubble_height + 6):
            if is_own:
                # Own message - Classic XP Blue gradient
                # Drop shadow (bottom-right offset)
                dpg.draw_rectangle((4, 4), (bubble_width + 4, bubble_height + 4),
                                   fill=(80, 80, 100, 120), rounding=8)

                # Main bubble border (dark blue outline)
                dpg.draw_rectangle((0, 0), (bubble_width, bubble_height),
                                   color=(0, 78, 152, 255),
                                   rounding=8, thickness=2)

                # Top gradient section (lighter blue)
                dpg.draw_rectangle((2, 2), (bubble_width - 2, bubble_height // 2),
                                   fill=(166, 202, 240, 255), rounding=6)

                # Bottom gradient section (darker blue)
                dpg.draw_rectangle((2, bubble_height // 2), (bubble_width - 2, bubble_height - 2),
                                   fill=(49, 106, 197, 255), rounding=6)

                # Glossy highlight at top
                dpg.draw_rectangle((4, 4), (bubble_width - 4, 16),
                                   fill=(220, 235, 252, 150), rounding=6)

                text_color = (255, 255, 255, 255)
                time_color = (200, 220, 245, 255)
            else:
                # Others' message - Classic XP Gray/Silver gradient
                # Drop shadow
                dpg.draw_rectangle((4, 4), (bubble_width + 4, bubble_height + 4),
                                   fill=(60, 60, 60, 120), rounding=8)

                # Main bubble border (gray outline)
                dpg.draw_rectangle((0, 0), (bubble_width, bubble_height),
                                   color=(112, 112, 112, 255),
                                   rounding=8, thickness=2)

                # Top gradient section (light gray)
                dpg.draw_rectangle((2, 2), (bubble_width - 2, bubble_height // 2),
                                   fill=(235, 235, 235, 255), rounding=6)

                # Bottom gradient section (darker gray)
                dpg.draw_rectangle((2, bubble_height // 2), (bubble_width - 2, bubble_height - 2),
                                   fill=(192, 192, 192, 255), rounding=6)

                # Glossy highlight at top
                dpg.draw_rectangle((4, 4), (bubble_width - 4, 16),
                                   fill=(250, 250, 252, 180), rounding=6)

                text_color = (0, 0, 0, 255)
                time_color = (80, 80, 80, 255)

            # Message text with shadow for depth
            y_offset = 12
            for line in lines_in_msg:
                # Text shadow
                dpg.draw_text((16, y_offset + 1), line,
                              color=(0, 0, 0, 60), size=13)
                # Main text
                dpg.draw_text((15, y_offset), line,
                              color=text_color, size=13)
                y_offset += 20

            # Timestamp with shadow
            dpg.draw_text((bubble_width - 54, bubble_height - 19), time,
                          color=(0, 0, 0, 40), size=10)
            dpg.draw_text((bubble_width - 55, bubble_height - 20), time,
                          color=time_color, size=10)

# === HELPER FUNCTIONS ===

def node_id_from_dialog(dialog_id):
    """Extract node_id from dialog_id"""
    return dialog_id.replace("dialog_", "")


def confirm_delete_single(dialog_id, node_id, chat_name, msg_idx):
    """Confirm before deleting a single message"""
    confirm_id = "delete_confirm_single"

    if dpg.does_item_exist(confirm_id):
        dpg.delete_item(confirm_id)

    with dpg.window(label="Delete Message", tag=confirm_id, modal=True,
                    width=350, height=130, pos=[350, 300]):
        dpg.add_text("Delete this message?", color=(255, 200, 100))
        dpg.add_text("This action cannot be undone.", color=(200, 150, 150))
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="🗑️ Delete", width=140,
                           callback=lambda: [delete_single_message(dialog_id, node_id, chat_name, msg_idx),
                                             dpg.delete_item(confirm_id)])
            dpg.add_button(label="Cancel", width=140,
                           callback=lambda: dpg.delete_item(confirm_id))


def delete_single_message(dialog_id, node_id, chat_name, msg_idx):
    """Delete a single message from chat"""
    # Read chat
    chat_content = read_chat(chat_name)
    lines = chat_content.strip().split('\n')

    # Remove the line
    if 0 <= msg_idx < len(lines):
        del lines[msg_idx]

        # Write back
        filepath = os.path.join(CHATS_DIR, f"{chat_name}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

        # Refresh display
        refresh_enhanced_chat(node_id, chat_name, dialog_id)
        show_notification("✓ Message deleted", (255, 150, 100))
    else:
        show_notification("⚠️ Failed to delete", (255, 100, 100))


def forward_single_message(chat_name, username, message):
    """Forward a single message to another chat"""
    forward_id = "forward_single_dialog"

    if dpg.does_item_exist(forward_id):
        dpg.delete_item(forward_id)

    # Get all available chats
    available_chats = [c for c in app_state.chat_settings.keys() if c != chat_name]

    with dpg.window(label="Forward Message", tag=forward_id, modal=True,
                    width=450, height=350, pos=[250, 200]):
        dpg.add_text("Forward to:", color=(150, 200, 255))
        dpg.add_separator()

        preview = message[:100] + "..." if len(message) > 100 else message
        dpg.add_text(f'"{preview}"', color=(200, 200, 200), wrap=420)
        dpg.add_separator()

        dpg.add_text("Select destination chat:")

        with dpg.child_window(width=-1, height=180, border=True):
            if not available_chats:
                dpg.add_text("No other chats available", color=(150, 150, 150))
            else:
                for chat in available_chats:
                    chat_settings = app_state.chat_settings.get(chat, {})
                    icon = "👥" if chat_settings.get("is_group") else "💬"
                    dpg.add_checkbox(label=f"{icon} {chat}", tag=f"fwd_{chat}")

        dpg.add_separator()
        dpg.add_text("", tag="forward_msg_status")

        with dpg.group(horizontal=True):
            dpg.add_button(label="➤ Forward", width=180,
                           callback=lambda: execute_single_forward(chat_name, username,
                                                                   message, available_chats,
                                                                   forward_id))
            dpg.add_button(label="Cancel", width=180,
                           callback=lambda: dpg.delete_item(forward_id))


def execute_single_forward(source_chat, original_author, message, available_chats, dialog_id):
    """Execute forwarding of a single message"""
    # Find selected chats
    selected = []
    for chat in available_chats:
        check_id = f"fwd_{chat}"
        if dpg.does_item_exist(check_id) and dpg.get_value(check_id):
            selected.append(chat)

    if not selected:
        dpg.set_value("forward_msg_status", "⚠️ Select at least one chat")
        dpg.configure_item("forward_msg_status", color=(255, 200, 100))
        return

    # Forward to each selected chat
    for dest_chat in selected:
        forward_text = f"[Forwarded from {source_chat}] {original_author}: {message}"
        write_message(dest_chat, forward_text, app_state.current_user)

    dpg.set_value("forward_msg_status", f"✓ Forwarded to {len(selected)} chat(s)!")
    dpg.configure_item("forward_msg_status", color=(100, 255, 100))

    # Close after delay
    dpg.set_frame_callback(60, lambda: dpg.delete_item(dialog_id)
    if dpg.does_item_exist(dialog_id) else None)


def save_single_message(chat_name, username, message):
    """Save a single message to saved messages"""
    try:
        from chat.saved_messages import save_message_to_saved
        save_message_to_saved(message, chat_name, username)
        show_notification("✓ Saved to Saved Messages", (100, 255, 100))
    except ImportError:
        # Fallback if saved_messages module not available
        show_notification("⚠️ Saved messages feature unavailable", (255, 200, 100))


def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        import pyperclip
        pyperclip.copy(text)
        show_notification("✓ Copied to clipboard", (100, 255, 100))
    except:
        # Fallback - just show the text was "copied"
        show_notification("✓ Text copied", (100, 255, 100))


def set_reply_to(dialog_id, username, message):
    """Set reply state and show reply bar"""
    reply_state[dialog_id] = {"username": username, "message": message}

    if dpg.does_item_exist(f"reply_bar_{dialog_id}"):
        dpg.configure_item(f"reply_bar_{dialog_id}", show=True)

    if dpg.does_item_exist(f"reply_to_{dialog_id}"):
        dpg.set_value(f"reply_to_{dialog_id}", f"Replying to {username}")

    if dpg.does_item_exist(f"reply_preview_{dialog_id}"):
        preview = message[:80] + "..." if len(message) > 80 else message
        dpg.set_value(f"reply_preview_{dialog_id}", preview)


def cancel_reply(dialog_id):
    """Cancel reply and hide bar"""
    reply_state[dialog_id] = None

    if dpg.does_item_exist(f"reply_bar_{dialog_id}"):
        dpg.configure_item(f"reply_bar_{dialog_id}", show=False)


def send_message(node_id, chat_name, dialog_id):
    """Send message with reply support"""
    input_tag = f"input_{node_id}"

    if not dpg.does_item_exist(input_tag):
        show_notification("⚠️ Cannot send message", (255, 100, 100))
        return

    message = dpg.get_value(input_tag).strip()

    if not message:
        show_notification("⚠️ Message is empty", (255, 200, 100))
        return

    # Check if replying
    if dialog_id in reply_state and reply_state[dialog_id]:
        reply_info = reply_state[dialog_id]
        message = f"↩️ @{reply_info['username']}: {message}"
        cancel_reply(dialog_id)

    write_message(chat_name, message, app_state.current_user)
    dpg.set_value(input_tag, "")
    refresh_enhanced_chat(node_id, chat_name, dialog_id)
    show_notification("✓ Message sent", (100, 255, 100))


def refresh_enhanced_chat(node_id, chat_name, dialog_id):
    """Refresh chat display"""
    scroll_id = f"chat_scroll_{node_id}"

    if dpg.does_item_exist(scroll_id):
        dpg.delete_item(scroll_id, children_only=True)
        display_enhanced_chat(node_id, chat_name, dialog_id)


def insert_text(node_id, text):
    """Insert text at cursor position"""
    input_tag = f"input_{node_id}"
    current = dpg.get_value(input_tag)
    dpg.set_value(input_tag, current + text)


def show_notification(message, color=(100, 255, 100)):
    """Show temporary notification"""
    notif_id = "chat_notification_toast"

    if dpg.does_item_exist(notif_id):
        dpg.delete_item(notif_id)

    with dpg.window(label="", tag=notif_id,
                    width=320, height=70, pos=[720, 650],
                    no_title_bar=True, no_resize=True, no_move=True,
                    popup=True, no_scrollbar=True):
        with dpg.drawlist(width=300, height=50):
            dpg.draw_rectangle((0, 0), (300, 50),
                               fill=(47, 49, 54, 255),
                               color=color, rounding=10, thickness=3)
            dpg.draw_text((20, 17), message, color=color, size=14)

    dpg.set_frame_callback(90, lambda: dpg.delete_item(notif_id)
    if dpg.does_item_exist(notif_id) else None)


def show_chat_info(chat_name, dialog_id):
    """Show chat information dialog"""
    info_id = "chat_info_dialog"

    if dpg.does_item_exist(info_id):
        dpg.delete_item(info_id)

    chat_settings = app_state.chat_settings.get(chat_name, {})
    author = chat_settings.get("author", "Unknown")
    is_group = chat_settings.get("is_group", False)
    read_only = chat_settings.get("read_only", False)
    members = chat_settings.get("members", [])

    # Count messages
    chat_content = read_chat(chat_name)
    message_count = len([l for l in chat_content.split('\n') if l.strip()])

    with dpg.window(label=f"ℹ️ Chat Info - {chat_name}", tag=info_id, modal=True,
                    width=400, height=350, pos=[280, 180]):

        with dpg.drawlist(width=380, height=60):
            dpg.draw_rectangle((0, 0), (380, 60), fill=(40, 45, 55, 255))
            icon = "👥" if is_group else "💬"
            dpg.draw_text((15, 15), f"{icon} {chat_name}",
                          color=(220, 220, 230), size=18)

        dpg.add_spacer(height=10)

        dpg.add_text("Chat Details:", color=(150, 200, 255))
        dpg.add_separator()

        dpg.add_text(f"Type: {'Group Chat' if is_group else 'Private Chat'}")
        dpg.add_text(f"Author: {author}", color=get_user_color(author))
        dpg.add_text(f"Read-only: {'Yes 🔒' if read_only else 'No ✏️'}")
        dpg.add_text(f"Total Messages: {message_count}")

        if is_group:
            dpg.add_separator()
            dpg.add_text(f"Members ({len(members)}):", color=(150, 200, 255))
            for member in members:
                member_color = get_user_color(member)
                dpg.add_text(f"  • {member}", color=member_color)

        dpg.add_separator()
        dpg.add_button(label="Close", width=150,
                       callback=lambda: dpg.delete_item(info_id))


def show_access_denied_dialog(chat_name):
    """Show access denied dialog"""
    dialog_id = "access_denied"
    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="Access Denied", tag=dialog_id, modal=True,
                    width=400, height=150, pos=[250, 200]):
        dpg.add_text(f"❌ You are not a member of '{chat_name}'",
                     color=(255, 100, 100))
        dpg.add_text("Only the author can add you to this group chat.")
        dpg.add_separator()
        dpg.add_button(label="OK", width=150,
                       callback=lambda: dpg.delete_item(dialog_id))


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

def show_member_management():
    """Show member management dialog"""
    """add this later"""
    pass


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

    result = create_chat_node(chat_name, read_only, is_group)

    if result:
        dpg.delete_item("create_chat_dialog")
    else:
        dpg.set_value("dialog_create_message", "Failed to create! Check console.")
        dpg.configure_item("dialog_create_message", color=(255, 0, 0))