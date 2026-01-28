# ===========================================
# FILE: ui/node_position_manager.py (UPDATED FOR FILES + MARKDOWN)
# ===========================================

import json
import os
import dearpygui.dearpygui as dpg
from config import app_state

POSITIONS_FILE = "node_positions.json"


def save_all_node_positions():
    """Save positions of all nodes to file"""
    positions_data = {
        "chats": {},
        "scripts": {},
        "highlights": {},
        "texts": {},
        "images": {},
        "audio": {},
        "files": {}  # NEW: File nodes
    }

    saved_count = 0

    # Save chat node positions WITH PROPERTIES
    for node_id, chat_name in app_state.node_chats.items():
        if dpg.does_item_exist(node_id):
            try:
                pos = dpg.get_item_pos(node_id)
                chat_settings = app_state.chat_settings.get(chat_name, {})

                positions_data["chats"][chat_name] = {
                    "pos": [float(pos[0]), float(pos[1])],
                    "read_only": chat_settings.get("read_only", False),
                    "is_group": chat_settings.get("is_group", False),
                    "members": chat_settings.get("members", []),
                    "author": chat_settings.get("author", app_state.current_user)
                }
                saved_count += 1
            except Exception as e:
                print(f"  Error saving chat '{chat_name}': {e}")

    # Save script node positions
    for script_name, node_id in app_state.script_nodes.items():
        if dpg.does_item_exist(node_id):
            try:
                pos = dpg.get_item_pos(node_id)
                positions_data["scripts"][script_name] = {
                    "pos": [float(pos[0]), float(pos[1])],
                }
                saved_count += 1
            except Exception as e:
                print(f"  Error saving script '{script_name}': {e}")

    # Save highlight box positions AND properties
    for label, node_id in app_state.highlight_boxes.items():
        if dpg.does_item_exist(node_id):
            try:
                pos = dpg.get_item_pos(node_id)
                props = getattr(app_state, 'highlight_properties', {}).get(label, {})
                width = props.get("width", 300)
                height = props.get("height", 200)
                color = props.get("color", [255, 255, 0, 50])

                positions_data["highlights"][label] = {
                    "pos": [float(pos[0]), float(pos[1])],
                    "width": width,
                    "height": height,
                    "color": color
                }
                saved_count += 1
            except Exception as e:
                print(f"  Error saving highlight '{label}': {e}")

    # Save text node positions AND markdown file paths
    for text_key, text_data in app_state.text_nodes.items():
        node_id = text_data["id"]
        if dpg.does_item_exist(node_id):
            try:
                pos = dpg.get_item_pos(node_id)
                positions_data["texts"][text_key] = {
                    "pos": [float(pos[0]), float(pos[1])],
                    "title": text_data["title"],
                    "filepath": text_data["filepath"],
                    "author": text_data["author"]
                }
                saved_count += 1
            except Exception as e:
                print(f"  Error saving text '{text_key}': {e}")

    # Save image node positions AND properties
    if hasattr(app_state, 'image_nodes'):
        for image_key, image_data in app_state.image_nodes.items():
            node_id = image_data["id"]
            if dpg.does_item_exist(node_id):
                try:
                    pos = dpg.get_item_pos(node_id)
                    positions_data["images"][image_key] = {
                        "pos": [float(pos[0]), float(pos[1])],
                        "label": image_data["label"],
                        "path": image_data["path"],
                        "width": image_data["width"],
                        "height": image_data["height"],
                        "author": image_data["author"]
                    }
                    saved_count += 1
                except Exception as e:
                    print(f"  Error saving image '{image_key}': {e}")

    # Save audio node positions AND properties
    if hasattr(app_state, 'audio_nodes'):
        for audio_key, audio_data in app_state.audio_nodes.items():
            node_id = audio_data["id"]
            if dpg.does_item_exist(node_id):
                try:
                    pos = dpg.get_item_pos(node_id)
                    positions_data["audio"][audio_key] = {
                        "pos": [float(pos[0]), float(pos[1])],
                        "label": audio_data["label"],
                        "path": audio_data["path"],
                        "author": audio_data["author"]
                    }
                    saved_count += 1
                except Exception as e:
                    print(f"  Error saving audio '{audio_key}': {e}")

    # Save file node positions AND properties (NEW)
    if hasattr(app_state, 'file_nodes'):
        for file_key, file_data in app_state.file_nodes.items():
            node_id = file_data["id"]
            if dpg.does_item_exist(node_id):
                try:
                    pos = dpg.get_item_pos(node_id)
                    positions_data["files"][file_key] = {
                        "pos": [float(pos[0]), float(pos[1])],
                        "label": file_data["label"],
                        "path": file_data["path"],
                        "author": file_data["author"],
                        "size": file_data["size"],
                        "extension": file_data["extension"]
                    }
                    saved_count += 1
                except Exception as e:
                    print(f"  Error saving file '{file_key}': {e}")

    try:
        with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(positions_data, f, indent=2)
        print(f"\n✓ Saved {saved_count} total node positions to {POSITIONS_FILE}")
        return True
    except Exception as e:
        print(f"ERROR saving node positions to file: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_all_node_positions():
    """Load and restore node positions from file - RECREATES missing nodes"""
    if not os.path.exists(POSITIONS_FILE):
        print(f"No saved positions file found at {POSITIONS_FILE}")
        return False

    try:
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            positions_data = json.load(f)

        print(f"\n=== Loading and recreating nodes from {POSITIONS_FILE} ===")
        loaded_count = 0

        # RECREATE chat nodes
        chat_data = positions_data.get("chats", {})
        print(f"Found {len(chat_data)} saved chat nodes")
        for chat_name, data in chat_data.items():
            found = False
            for node_id, stored_chat_name in app_state.node_chats.items():
                if stored_chat_name == chat_name and dpg.does_item_exist(node_id):
                    dpg.set_item_pos(node_id, data["pos"])
                    print(f"  ✓ Restored existing chat '{chat_name}' to position {data['pos']}")
                    loaded_count += 1
                    found = True
                    break

            if not found:
                try:
                    print(f"  🔧 Recreating chat node '{chat_name}'...")
                    _recreate_chat_node(
                        chat_name=chat_name,
                        position=data["pos"],
                        read_only=data.get("read_only", False),
                        is_group=data.get("is_group", False),
                        members=data.get("members", []),
                        author=data.get("author", app_state.current_user)
                    )
                    print(f"  ✓ Recreated chat '{chat_name}' at position {data['pos']}")
                    loaded_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to recreate chat '{chat_name}': {e}")

        # Restore script positions
        script_data = positions_data.get("scripts", {})
        print(f"Found {len(script_data)} saved script positions")
        for script_name, data in script_data.items():
            if script_name in app_state.script_nodes:
                node_id = app_state.script_nodes[script_name]
                if dpg.does_item_exist(node_id):
                    dpg.set_item_pos(node_id, data["pos"])
                    print(f"  ✓ Restored script '{script_name}' to position {data['pos']}")
                    loaded_count += 1

        # RECREATE highlight boxes
        highlight_data = positions_data.get("highlights", {})
        print(f"Found {len(highlight_data)} saved highlight boxes")
        for label, data in highlight_data.items():
            if label in app_state.highlight_boxes:
                node_id = app_state.highlight_boxes[label]
                if dpg.does_item_exist(node_id):
                    dpg.set_item_pos(node_id, data["pos"])
                    print(f"  ✓ Restored existing highlight '{label}' to position {data['pos']}")
                    loaded_count += 1
                    continue

            try:
                print(f"  🔧 Recreating highlight '{label}'...")
                _recreate_highlight_box(
                    label=label,
                    position=data["pos"],
                    width=data.get("width", 300),
                    height=data.get("height", 200),
                    color=data.get("color", [255, 255, 0, 50])
                )
                print(f"  ✓ Recreated highlight '{label}' at position {data['pos']}")
                loaded_count += 1
            except Exception as e:
                print(f"  ✗ Failed to recreate highlight '{label}': {e}")

        # RECREATE text nodes from markdown files
        text_data = positions_data.get("texts", {})
        print(f"Found {len(text_data)} saved text nodes")
        for text_key, data in text_data.items():
            if text_key in app_state.text_nodes:
                node_id = app_state.text_nodes[text_key]["id"]
                if dpg.does_item_exist(node_id):
                    dpg.set_item_pos(node_id, data["pos"])
                    print(f"  ✓ Restored existing text '{text_key}' to position {data['pos']}")
                    loaded_count += 1
                    continue

            try:
                print(f"  🔧 Recreating text node '{text_key}'...")
                _recreate_text_node(
                    title=data["title"],
                    filepath=data["filepath"],
                    position=data["pos"],
                    author=data.get("author", "Unknown")
                )
                print(f"  ✓ Recreated text node at position {data['pos']}")
                loaded_count += 1
            except Exception as e:
                print(f"  ✗ Failed to recreate text node '{text_key}': {e}")

        # RECREATE image nodes
        if hasattr(app_state, 'image_nodes'):
            image_data = positions_data.get("images", {})
            print(f"Found {len(image_data)} saved image nodes")
            for image_key, data in image_data.items():
                if image_key in app_state.image_nodes:
                    node_id = app_state.image_nodes[image_key]["id"]
                    if dpg.does_item_exist(node_id):
                        dpg.set_item_pos(node_id, data["pos"])
                        print(f"  ✓ Restored existing image '{image_key}' to position {data['pos']}")
                        loaded_count += 1
                        continue

                try:
                    print(f"  🔧 Recreating image node '{image_key}'...")
                    _recreate_image_node(
                        label=data["label"],
                        path=data["path"],
                        position=data["pos"],
                        width=data.get("width", 200),
                        height=data.get("height", 200),
                        author=data.get("author", "Unknown")
                    )
                    print(f"  ✓ Recreated image node at position {data['pos']}")
                    loaded_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to recreate image node '{image_key}': {e}")

        # RECREATE audio nodes
        if hasattr(app_state, 'audio_nodes'):
            audio_data = positions_data.get("audio", {})
            print(f"Found {len(audio_data)} saved audio nodes")
            for audio_key, data in audio_data.items():
                if audio_key in app_state.audio_nodes:
                    node_id = app_state.audio_nodes[audio_key]["id"]
                    if dpg.does_item_exist(node_id):
                        dpg.set_item_pos(node_id, data["pos"])
                        print(f"  ✓ Restored existing audio '{audio_key}' to position {data['pos']}")
                        loaded_count += 1
                        continue

                try:
                    print(f"  🔧 Recreating audio node '{audio_key}'...")
                    _recreate_audio_node(
                        label=data["label"],
                        path=data["path"],
                        position=data["pos"],
                        author=data.get("author", "Unknown")
                    )
                    print(f"  ✓ Recreated audio node at position {data['pos']}")
                    loaded_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to recreate audio node '{audio_key}': {e}")

        # RECREATE file nodes (NEW)
        if hasattr(app_state, 'file_nodes'):
            file_data = positions_data.get("files", {})
            print(f"Found {len(file_data)} saved file nodes")
            for file_key, data in file_data.items():
                if file_key in app_state.file_nodes:
                    node_id = app_state.file_nodes[file_key]["id"]
                    if dpg.does_item_exist(node_id):
                        dpg.set_item_pos(node_id, data["pos"])
                        print(f"  ✓ Restored existing file '{file_key}' to position {data['pos']}")
                        loaded_count += 1
                        continue

                try:
                    print(f"  🔧 Recreating file node '{file_key}'...")
                    _recreate_file_node(
                        label=data["label"],
                        path=data["path"],
                        position=data["pos"],
                        author=data.get("author", "Unknown"),
                        size=data.get("size", 0),
                        extension=data.get("extension", "")
                    )
                    print(f"  ✓ Recreated file node at position {data['pos']}")
                    loaded_count += 1
                except Exception as e:
                    print(f"  ✗ Failed to recreate file node '{file_key}': {e}")

        print(f"\n✓ Loaded/recreated {loaded_count} nodes successfully")
        return True

    except Exception as e:
        print(f"ERROR loading node positions: {e}")
        import traceback
        traceback.print_exc()
        return False


# Recreation functions
def _recreate_chat_node(chat_name, position, read_only=False, is_group=False, members=None, author=None):
    from chat.chat_manager import create_chat
    if members is None:
        members = []
    if author is None:
        author = app_state.current_user

    chat_settings = create_chat(chat_name, read_only, is_group)
    chat_settings["members"] = members
    chat_settings["author"] = author

    new_node_id = dpg.generate_uuid()
    app_state.node_chats[new_node_id] = chat_name

    label = ""
    if is_group:
        label += "👥 "
    if read_only:
        label += "🔒 "
    label += chat_name

    def delete_callback():
        if dpg.does_item_exist(new_node_id):
            dpg.delete_item(new_node_id)
        if new_node_id in app_state.node_chats:
            del app_state.node_chats[new_node_id]

    def open_chat_callback():
        try:
            from chat.ui import show_chat_dialog
            show_chat_dialog(None, None, new_node_id)
        except ImportError:
            print("Cannot open chat - chat.ui module not found")

    with dpg.node(label=label, pos=position, parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            icon = "👥" if is_group else "💬"
            with dpg.group(horizontal=True):
                dpg.add_text(f"{icon} {chat_name}")
                dpg.add_button(label="❌", width=30, callback=delete_callback)

            if read_only:
                dpg.add_text(f"🔒 Author: {author}", color=app_state.current_user_color)
            if is_group:
                dpg.add_text(f"Members: {len(members)}", color=(150, 200, 255))

            dpg.add_button(label="Open Chat", callback=open_chat_callback)


def _recreate_highlight_box(label, position, width, height, color):
    from nodes.highlight import create_highlight_box
    create_highlight_box(label, width, height, color)
    node_id = app_state.highlight_boxes.get(label)
    if node_id and dpg.does_item_exist(node_id):
        dpg.set_item_pos(node_id, position)


def _recreate_text_node(title, filepath, position, author):
    """Recreate text node from saved markdown file"""
    new_node_id = dpg.generate_uuid()

    # Check if file exists
    if not os.path.exists(filepath):
        print(f"Warning: Markdown file not found: {filepath}")
        return

    # Read content for preview
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        content = "Error loading content"

    text_key = f"text_{new_node_id}"
    app_state.text_nodes[text_key] = {
        "id": new_node_id,
        "title": title,
        "filepath": filepath,
        "author": author
    }

    # Create preview
    preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content.replace('\n', ' ')

    def delete_callback():
        if dpg.does_item_exist(new_node_id):
            dpg.delete_item(new_node_id)
        if text_key in app_state.text_nodes:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except:
                pass
            del app_state.text_nodes[text_key]

    def view_callback():
        try:
            from nodes.text import show_full_note
            show_full_note(text_key)
        except ImportError:
            print("Cannot view note - nodes.text module not found")

    def edit_callback():
        try:
            from nodes.text import edit_text_node
            edit_text_node(text_key)
        except ImportError:
            print("Cannot edit note - nodes.text module not found")

    with dpg.node(label=f"📝 {title}", pos=position,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.group(horizontal=True):
                dpg.add_text("Note", color=(255, 255, 100))
                dpg.add_button(label='""', width=30, callback=view_callback,
                               tag=f"view_btn_{new_node_id}")
                dpg.add_button(label="Edit", width=30, callback=edit_callback)
                dpg.add_button(label="Close", width=30, callback=delete_callback)

            dpg.add_separator()
            dpg.add_text(title, color=(200, 200, 255), wrap=250)
            dpg.add_separator()
            dpg.add_text(preview, tag=f"text_preview_{new_node_id}",
                         color=(180, 180, 180), wrap=250)
            dpg.add_separator()
            dpg.add_text(f"By: {author}", color=app_state.current_user_color)

    with dpg.tooltip(f"view_btn_{new_node_id}"):
        dpg.add_text("Click to view full note")


def _recreate_image_node(label, path, position, width, height, author):
    from nodes.image import create_image_node
    create_image_node(label, path, width, height)
    # Find the newly created node and set its position
    for image_key, image_data in app_state.image_nodes.items():
        if image_data["label"] == label and image_data["path"] == path:
            node_id = image_data["id"]
            if dpg.does_item_exist(node_id):
                dpg.set_item_pos(node_id, position)
            break


def _recreate_audio_node(label, path, position, author):
    from nodes.audio import create_audio_node
    create_audio_node(label, path)
    # Find the newly created node and set its position
    for audio_key, audio_data in app_state.audio_nodes.items():
        if audio_data["label"] == label and audio_data["path"] == path:
            node_id = audio_data["id"]
            if dpg.does_item_exist(node_id):
                dpg.set_item_pos(node_id, position)
            break


def _recreate_file_node(label, path, position, author, size, extension):
    """Recreate file node from saved data (NEW)"""
    new_node_id = dpg.generate_uuid()

    # Check if file exists
    if not os.path.exists(path):
        print(f"Warning: File not found: {path}")
        return

    # Import file node functions
    try:
        from nodes.file import get_file_type_info, format_file_size, open_file, save_file_as, edit_file_node, \
            delete_file_node
    except ImportError:
        print("Cannot recreate file node - nodes.file module not found")
        return

    # Get file info
    if size == 0:
        size = os.path.getsize(path)
    file_size_str = format_file_size(size)

    if not extension:
        extension = os.path.splitext(path)[1].upper()[1:]

    file_info = get_file_type_info(path)

    # Store file data
    file_key = f"file_{new_node_id}"
    if not hasattr(app_state, 'file_nodes'):
        app_state.file_nodes = {}

    app_state.file_nodes[file_key] = {
        "id": new_node_id,
        "label": label,
        "path": path,
        "author": author,
        "size": size,
        "extension": extension
    }

    # Shorter label for display
    display_label = label[:18] + "..." if len(label) > 18 else label

    # Create minimalistic node
    with dpg.node(label=f"{file_info['icon']} {display_label}", pos=position,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            # Title bar with controls
            with dpg.group(horizontal=True):
                dpg.add_text(file_info['icon'], color=file_info['color'])
                dpg.add_text(label, color=file_info['color'], wrap=180)

            dpg.add_separator()

            # File info
            with dpg.group(horizontal=True):
                dpg.add_text(f"Type: {extension}", color=(150, 150, 150))
                dpg.add_text(f"Size: {file_size_str}", color=(150, 150, 150))

            dpg.add_separator()

            # Action buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="📂 Open", width=60, height=22,
                               callback=lambda: open_file(file_key),
                               tag=f"open_btn_{new_node_id}")
                dpg.add_button(label="💾 Save As", width=70, height=22,
                               callback=lambda: save_file_as(file_key))
                dpg.add_button(label="✏️", width=25, height=22,
                               callback=lambda: edit_file_node(file_key))
                dpg.add_button(label="❌", width=25, height=22,
                               callback=lambda: delete_file_node(new_node_id, file_key))

            dpg.add_separator()
            dpg.add_text(f"By: {author}",
                         color=app_state.current_user_color, wrap=200)

    # Add tooltip
    with dpg.tooltip(f"open_btn_{new_node_id}"):
        dpg.add_text(f"Open {extension} file with default app")


def debug_print_app_state():
    """Debug function to print current app state"""
    print("\n=== APP STATE DEBUG ===")
    print(f"node_chats: {app_state.node_chats}")
    print(f"script_nodes: {app_state.script_nodes}")
    print(f"highlight_boxes: {app_state.highlight_boxes}")
    print(f"text_nodes keys: {list(app_state.text_nodes.keys()) if app_state.text_nodes else 'empty'}")
    if hasattr(app_state, 'image_nodes'):
        print(f"image_nodes keys: {list(app_state.image_nodes.keys()) if app_state.image_nodes else 'empty'}")
    if hasattr(app_state, 'audio_nodes'):
        print(f"audio_nodes keys: {list(app_state.audio_nodes.keys()) if app_state.audio_nodes else 'empty'}")
    if hasattr(app_state, 'file_nodes'):
        print(f"file_nodes keys: {list(app_state.file_nodes.keys()) if app_state.file_nodes else 'empty'}")