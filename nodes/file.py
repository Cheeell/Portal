# ===========================================
# FILE: nodes/file.py (NEW - GENERIC FILE HANDLER)
# ===========================================

import dearpygui.dearpygui as dpg
import random
import os
import subprocess
import platform
from config import app_state

# Directory for storing files
FILES_DIR = "files"
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# File type icons and colors
FILE_TYPE_INFO = {
    '.pdf': {'icon': '📄', 'color': (255, 100, 100)},
    '.doc': {'icon': '📝', 'color': (100, 150, 255)},
    '.docx': {'icon': '📝', 'color': (100, 150, 255)},
    '.xls': {'icon': '📊', 'color': (100, 255, 100)},
    '.xlsx': {'icon': '📊', 'color': (100, 255, 100)},
    '.ppt': {'icon': '📊', 'color': (255, 200, 100)},
    '.pptx': {'icon': '📊', 'color': (255, 200, 100)},
    '.txt': {'icon': '📃', 'color': (200, 200, 200)},
    '.zip': {'icon': '📦', 'color': (255, 200, 0)},
    '.rar': {'icon': '📦', 'color': (255, 200, 0)},
    '.7z': {'icon': '📦', 'color': (255, 200, 0)},
    '.tar': {'icon': '📦', 'color': (255, 200, 0)},
    '.gz': {'icon': '📦', 'color': (255, 200, 0)},
    '.mp4': {'icon': '🎥', 'color': (200, 100, 255)},
    '.avi': {'icon': '🎥', 'color': (200, 100, 255)},
    '.mkv': {'icon': '🎥', 'color': (200, 100, 255)},
    '.mov': {'icon': '🎥', 'color': (200, 100, 255)},
    '.csv': {'icon': '📋', 'color': (100, 255, 200)},
    '.json': {'icon': '📋', 'color': (100, 255, 200)},
    '.xml': {'icon': '📋', 'color': (100, 255, 200)},
    '.html': {'icon': '🌐', 'color': (255, 150, 100)},
    '.css': {'icon': '🎨', 'color': (100, 200, 255)},
    '.js': {'icon': '⚙️', 'color': (255, 220, 100)},
    'default': {'icon': '📎', 'color': (150, 150, 150)}
}


def get_file_type_info(filepath):
    """Get icon and color for a file type"""
    ext = os.path.splitext(filepath)[1].lower()
    return FILE_TYPE_INFO.get(ext, FILE_TYPE_INFO['default'])


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def show_add_file_dialog():
    """Show file dialog to add any file type"""
    if dpg.does_item_exist("file_file_dialog"):
        dpg.delete_item("file_file_dialog")

    with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=file_selected_auto,
            tag="file_file_dialog",
            width=700,
            height=400,
            modal=True,
            default_path=os.path.expanduser("~")
    ):
        dpg.add_file_extension(".*", color=(150, 150, 150, 255))
        dpg.add_file_extension(".pdf", color=(255, 100, 100, 255))
        dpg.add_file_extension(".doc", color=(100, 150, 255, 255))
        dpg.add_file_extension(".docx", color=(100, 150, 255, 255))
        dpg.add_file_extension(".xls", color=(100, 255, 100, 255))
        dpg.add_file_extension(".xlsx", color=(100, 255, 100, 255))
        dpg.add_file_extension(".zip", color=(255, 200, 0, 255))
        dpg.add_file_extension(".rar", color=(255, 200, 0, 255))
        dpg.add_file_extension(".mp4", color=(200, 100, 255, 255))
        dpg.add_file_extension(".avi", color=(200, 100, 255, 255))


def file_selected_auto(sender, app_data):
    """Handle file selection - automatically create node"""
    if not app_data["selections"]:
        return

    filepath = list(app_data["selections"].values())[0]
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return

    # Check if it's an image or audio file (already have dedicated nodes)
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
        show_notification("⚠️ Use 'Add Image' for image files", (255, 200, 100))
        return
    if ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']:
        show_notification("⚠️ Use 'Add Audio' for audio files", (255, 200, 100))
        return

    # Use filename (without extension) as default label
    label = os.path.splitext(filename)[0]

    # Copy file to files directory
    import shutil
    dest_path = os.path.join(FILES_DIR, filename)

    # Handle duplicate filenames
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(FILES_DIR, filename)
        counter += 1

    try:
        shutil.copy2(filepath, dest_path)
        create_file_node(label, dest_path)
        print(f"✓ File added: {label}")
        show_notification(f"✓ File added: {label}", (100, 255, 100))
    except Exception as e:
        print(f"Error adding file: {e}")
        show_notification(f"⚠️ Error: {e}", (255, 100, 100))


def create_file_node(label, file_path):
    """Create a file node on the board"""
    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()

    # Get file info
    file_size = os.path.getsize(file_path)
    file_size_str = format_file_size(file_size)
    file_ext = os.path.splitext(file_path)[1].upper()[1:]  # Remove the dot
    file_info = get_file_type_info(file_path)

    # Store file data
    file_key = f"file_{new_node_id}"
    if not hasattr(app_state, 'file_nodes'):
        app_state.file_nodes = {}

    app_state.file_nodes[file_key] = {
        "id": new_node_id,
        "label": label,
        "path": file_path,
        "author": app_state.current_user,
        "size": file_size,
        "extension": file_ext
    }

    # Shorter label for display
    display_label = label[:18] + "..." if len(label) > 18 else label

    # Create minimalistic node
    with dpg.node(label=f"{file_info['icon']} {display_label}", pos=pos,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            # Title bar with controls
            with dpg.group(horizontal=True):
                dpg.add_text(file_info['icon'], color=file_info['color'])
                dpg.add_text(label, color=file_info['color'], wrap=180)

            dpg.add_separator()

            # File info
            with dpg.group(horizontal=True):
                dpg.add_text(f"Type: {file_ext}", color=(150, 150, 150))
                dpg.add_text(f"Size: {file_size_str}", color=(150, 150, 150))

            dpg.add_separator()

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Open", width=60, height=22,
                               callback=lambda: open_file(file_key),
                               tag=f"open_btn_{new_node_id}")
                dpg.add_button(label="Save As", width=70, height=22,
                               callback=lambda: save_file_as(file_key))
                dpg.add_button(label="✏Edit", width=25, height=22,
                               callback=lambda: edit_file_node(file_key))
                dpg.add_button(label="Close", width=25, height=22,
                               callback=lambda: delete_file_node(new_node_id, file_key))

            dpg.add_separator()
            dpg.add_text(f"By: {app_state.current_user}",
                         color=app_state.current_user_color, wrap=200)

    # Add tooltip
    with dpg.tooltip(f"open_btn_{new_node_id}"):
        dpg.add_text(f"Open {file_ext} file with default app")


def open_file(file_key):
    """Open file with default system application"""
    if not hasattr(app_state, 'file_nodes') or file_key not in app_state.file_nodes:
        return

    file_data = app_state.file_nodes[file_key]
    file_path = file_data["path"]

    if not os.path.exists(file_path):
        show_notification("⚠️ File not found!", (255, 100, 100))
        return

    try:
        # Platform-specific file opening
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux and others
            subprocess.run(['xdg-open', file_path])

        show_notification(f"✓ Opening {file_data['label']}", (100, 255, 100))
    except Exception as e:
        print(f"Error opening file: {e}")
        show_notification(f"⚠️ Could not open file: {e}", (255, 100, 100))


def save_file_as(file_key):
    """Save file to a user-selected location"""
    if not hasattr(app_state, 'file_nodes') or file_key not in app_state.file_nodes:
        return

    file_data = app_state.file_nodes[file_key]
    original_filename = os.path.basename(file_data["path"])

    # Create save dialog
    save_dialog_id = f"save_file_dialog_{file_key}"

    if dpg.does_item_exist(save_dialog_id):
        dpg.delete_item(save_dialog_id)

    with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=lambda s, a, u=file_key: execute_save_as(u, a),
            tag=save_dialog_id,
            default_filename=original_filename,
            width=700,
            height=400,
            modal=True,
            file_count=1
    ):
        dpg.add_file_extension(".*")


def execute_save_as(file_key, app_data):
    """Execute the save as operation"""
    if not app_data or "file_path_name" not in app_data:
        return

    file_data = app_state.file_nodes[file_key]
    source_path = file_data["path"]
    dest_path = app_data["file_path_name"]

    try:
        import shutil
        shutil.copy2(source_path, dest_path)
        show_notification(f"✓ File saved to {os.path.basename(dest_path)}", (100, 255, 100))
    except Exception as e:
        print(f"Error saving file: {e}")
        show_notification(f"⚠️ Save failed: {e}", (255, 100, 100))


def edit_file_node(file_key):
    """Edit file node properties"""
    if not hasattr(app_state, 'file_nodes') or file_key not in app_state.file_nodes:
        return

    file_data = app_state.file_nodes[file_key]
    editor_id = f"edit_file_{file_key}"

    if dpg.does_item_exist(editor_id):
        dpg.delete_item(editor_id)

    with dpg.window(label=f"Edit File: {file_data['label']}", tag=editor_id,
                    modal=True, width=400, height=200, pos=[250, 200]):

        dpg.add_text("Edit file properties:")
        dpg.add_separator()

        dpg.add_text("Label:")
        dpg.add_input_text(tag=f"edit_label_{file_key}", width=370,
                           default_value=file_data['label'])

        dpg.add_separator()
        dpg.add_text(f"File: {os.path.basename(file_data['path'])}", color=(150, 150, 150))
        dpg.add_text(f"Size: {format_file_size(file_data['size'])}", color=(150, 150, 150))

        dpg.add_separator()
        dpg.add_text("", tag=f"edit_message_{file_key}")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", width=150,
                           callback=lambda: save_file_edit(file_key, editor_id))
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(editor_id))


def save_file_edit(file_key, editor_id):
    """Save changes to file node"""
    if not hasattr(app_state, 'file_nodes') or file_key not in app_state.file_nodes:
        return

    new_label = dpg.get_value(f"edit_label_{file_key}").strip()

    if not new_label:
        dpg.set_value(f"edit_message_{file_key}", "Please enter a label!")
        dpg.configure_item(f"edit_message_{file_key}", color=(255, 0, 0))
        return

    file_data = app_state.file_nodes[file_key]
    node_id = file_data["id"]

    # Update stored data
    file_data["label"] = new_label

    # Update node label
    if dpg.does_item_exist(node_id):
        file_info = get_file_type_info(file_data["path"])
        display_label = new_label[:18] + "..." if len(new_label) > 18 else new_label
        dpg.configure_item(node_id, label=f"{file_info['icon']} {display_label}")

    dpg.delete_item(editor_id)
    show_notification("✓ File updated", (100, 255, 100))


def delete_file_node(node_id, file_key):
    """Delete a file node"""
    if not hasattr(app_state, 'file_nodes') or file_key not in app_state.file_nodes:
        return

    # Delete the node from UI
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    # Delete from state (file stays in files/ directory)
    if file_key in app_state.file_nodes:
        del app_state.file_nodes[file_key]

    show_notification("✓ File node removed", (100, 255, 100))


def show_notification(message, color=(100, 255, 100)):
    """Show a temporary notification"""
    notif_id = "file_notification"

    if dpg.does_item_exist(notif_id):
        dpg.delete_item(notif_id)

    with dpg.window(label="", tag=notif_id,
                    width=350, height=80, pos=[500, 100],
                    no_title_bar=True, no_resize=True, no_move=True,
                    popup=True):
        with dpg.drawlist(width=330, height=60):
            dpg.draw_rectangle((0, 0), (330, 60), fill=(35, 35, 40, 255),
                               color=color, rounding=8, thickness=2)
            dpg.draw_text((20, 20), message, color=color, size=13)

    # Auto-close after 2 seconds
    dpg.set_frame_callback(60, lambda: dpg.delete_item(notif_id) if dpg.does_item_exist(notif_id) else None)