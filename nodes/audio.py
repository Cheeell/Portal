# ===========================================
# FILE: nodes/audio.py (MINIMALISTIC DESIGN)
# ===========================================

import dearpygui.dearpygui as dpg
import random
import os
import threading
from config import app_state

# Directory for storing audio files
AUDIO_DIR = "audio"
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)


def show_add_audio_dialog():
    """Show file dialog directly - audio is added automatically after selection"""
    if dpg.does_item_exist("audio_file_dialog"):
        dpg.delete_item("audio_file_dialog")

    with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=audio_file_selected_auto,
            tag="audio_file_dialog",
            width=700,
            height=400,
            modal=True,
            default_path=os.path.expanduser("~")
    ):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".mp3", color=(100, 255, 100, 255))
        dpg.add_file_extension(".wav", color=(100, 200, 255, 255))
        dpg.add_file_extension(".ogg", color=(255, 200, 100, 255))
        dpg.add_file_extension(".flac", color=(255, 150, 255, 255))
        dpg.add_file_extension(".m4a", color=(150, 255, 150, 255))


def audio_file_selected_auto(sender, app_data):
    """Handle audio file selection - automatically create node"""
    if not app_data["selections"]:
        return

    filepath = list(app_data["selections"].values())[0]
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return

    # Use filename (without extension) as default label
    label = os.path.splitext(filename)[0]

    # Copy audio to audio directory
    import shutil
    dest_path = os.path.join(AUDIO_DIR, filename)

    # Handle duplicate filenames
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(AUDIO_DIR, filename)
        counter += 1

    try:
        shutil.copy2(filepath, dest_path)
        create_audio_node(label, dest_path)
        print(f"✓ Audio added: {label}")
    except Exception as e:
        print(f"Error adding audio: {e}")


def create_audio_node(label, audio_path):
    """Create a minimalistic audio node on the board"""
    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()

    # Get file info
    file_size = os.path.getsize(audio_path)
    file_size_mb = file_size / (1024 * 1024)
    file_ext = os.path.splitext(audio_path)[1].upper()[1:]  # Remove the dot

    # Store audio data
    audio_key = f"audio_{new_node_id}"
    if not hasattr(app_state, 'audio_nodes'):
        app_state.audio_nodes = {}

    app_state.audio_nodes[audio_key] = {
        "id": new_node_id,
        "label": label,
        "path": audio_path,
        "author": app_state.current_user,
        "is_playing": False,
        "playback_thread": None
    }

    # Shorter label for display
    display_label = label[:20] + "..." if len(label) > 20 else label

    # Create minimalistic node
    with dpg.node(label=f"{display_label}", pos=pos,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            # Single line: title + controls
            with dpg.group(horizontal=True):
                dpg.add_text("play", color=(100, 255, 100),
                             tag=f"play_icon_{new_node_id}")
                dpg.add_button(label="play", width=60, height=20,
                               callback=lambda: toggle_audio(audio_key),
                               tag=f"play_btn_{new_node_id}")
                dpg.add_button(label="edit", width=25, height=20,
                               callback=lambda: edit_audio_node(audio_key))
                dpg.add_button(label="X", width=25, height=20,
                               callback=lambda: delete_audio_node(new_node_id, audio_key))

    # Update button label
    update_play_button(audio_key)


def toggle_audio(audio_key):
    """Toggle play/stop audio"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    audio_data = app_state.audio_nodes[audio_key]

    if audio_data.get("is_playing", False):
        stop_audio(audio_key)
    else:
        play_audio(audio_key)


def update_play_button(audio_key):
    """Update the play button text"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    audio_data = app_state.audio_nodes[audio_key]
    node_id = audio_data["id"]

    is_playing = audio_data.get("is_playing", False)

    if dpg.does_item_exist(f"play_btn_{node_id}"):
        if is_playing:
            dpg.configure_item(f"play_btn_{node_id}", label="stop")
            if dpg.does_item_exist(f"play_icon_{node_id}"):
                dpg.configure_item(f"play_icon_{node_id}", default_value="", color=(255, 100, 100))
        else:
            dpg.configure_item(f"play_btn_{node_id}", label="play")
            if dpg.does_item_exist(f"play_icon_{node_id}"):
                dpg.configure_item(f"play_icon_{node_id}", default_value="", color=(100, 255, 100))


def play_audio(audio_key):
    """Play audio file using pygame"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    audio_data = app_state.audio_nodes[audio_key]
    node_id = audio_data["id"]
    audio_path = audio_data["path"]

    try:
        import pygame

        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Update status
        audio_data["is_playing"] = True
        update_play_button(audio_key)

        # Play audio in a separate thread
        def play_thread():
            try:
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                # Update status when finished
                audio_data["is_playing"] = False
                update_play_button(audio_key)

            except Exception as e:
                print(f"Error during playback: {e}")
                audio_data["is_playing"] = False
                update_play_button(audio_key)

        playback_thread = threading.Thread(target=play_thread, daemon=True)
        playback_thread.start()
        audio_data["playback_thread"] = playback_thread

    except ImportError:
        print("Error: pygame not installed. Install with: pip install pygame")
        audio_data["is_playing"] = False
        update_play_button(audio_key)
    except Exception as e:
        print(f"Error playing audio: {e}")
        audio_data["is_playing"] = False
        update_play_button(audio_key)


def stop_audio(audio_key):
    """Stop audio playback"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    audio_data = app_state.audio_nodes[audio_key]

    try:
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

        audio_data["is_playing"] = False
        update_play_button(audio_key)

    except ImportError:
        pass
    except Exception as e:
        print(f"Error stopping audio: {e}")


def edit_audio_node(audio_key):
    """Edit an existing audio node"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    audio_data = app_state.audio_nodes[audio_key]
    editor_id = f"edit_audio_{audio_key}"

    if dpg.does_item_exist(editor_id):
        dpg.delete_item(editor_id)

    with dpg.window(label=f"Edit Audio: {audio_data['label']}", tag=editor_id,
                    modal=True, width=400, height=200, pos=[250, 200]):

        dpg.add_text("Edit audio properties:")
        dpg.add_separator()

        dpg.add_text("Label:")
        dpg.add_input_text(tag=f"edit_label_{audio_key}", width=370,
                           default_value=audio_data['label'])

        dpg.add_separator()
        dpg.add_text("", tag=f"edit_message_{audio_key}")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", width=150,
                           callback=lambda: save_audio_edit(audio_key, editor_id))
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(editor_id))


def save_audio_edit(audio_key, editor_id):
    """Save changes to audio node"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    new_label = dpg.get_value(f"edit_label_{audio_key}").strip()

    if not new_label:
        dpg.set_value(f"edit_message_{audio_key}", "Please enter a label!")
        dpg.configure_item(f"edit_message_{audio_key}", color=(255, 0, 0))
        return

    audio_data = app_state.audio_nodes[audio_key]
    node_id = audio_data["id"]

    # Update stored data
    audio_data["label"] = new_label

    # Update node label
    if dpg.does_item_exist(node_id):
        display_label = new_label[:20] + "..." if len(new_label) > 20 else new_label
        dpg.configure_item(node_id, label=f"🔊 {display_label}")

    dpg.delete_item(editor_id)


def delete_audio_node(node_id, audio_key):
    """Delete an audio node"""
    if not hasattr(app_state, 'audio_nodes') or audio_key not in app_state.audio_nodes:
        return

    # Stop playback if playing
    stop_audio(audio_key)

    # Delete the node from UI
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    # Delete from state
    if audio_key in app_state.audio_nodes:
        del app_state.audio_nodes[audio_key]