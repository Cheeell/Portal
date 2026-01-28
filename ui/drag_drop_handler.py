# ===========================================
# FILE: ui/drag_drop_handler.py
# ===========================================
import dearpygui.dearpygui as dpg
import os
from config import app_state


def setup_drag_drop_handlers():
    """Setup drag and drop handlers for the node editor"""
    if not dpg.does_item_exist(app_state.node_editor):
        print("Cannot setup drag-drop: node editor doesn't exist")
        return

    # Register drop callback for node editor
    with dpg.handler_registry():
        dpg.add_file_drop_handler(callback=handle_file_drop)

    print("✓ Drag and drop handlers registered")


def handle_file_drop(sender, app_data):
    """Handle files dropped onto the window"""
    dropped_files = app_data

    if not dropped_files:
        return

    print(f"\n=== Files dropped: {len(dropped_files)} ===")

    for file_path in dropped_files:
        print(f"Processing: {file_path}")

        if not os.path.exists(file_path):
            print(f"  ✗ File not found: {file_path}")
            continue

        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Determine file type and handle accordingly
        if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
            handle_image_drop(file_path)
        elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']:
            handle_audio_drop(file_path)
        elif ext in ['.py']:
            handle_script_drop(file_path)
        elif ext in ['.txt', '.md', '.markdown']:
            handle_text_drop(file_path)
        else:
            print(f"  ⚠️ Unsupported file type: {ext}")
            show_unsupported_file_notification(file_path)


def handle_image_drop(file_path):
    """Handle dropped image file"""
    try:
        from nodes.image import create_image_node
        import shutil

        filename = os.path.basename(file_path)
        label = os.path.splitext(filename)[0]

        # Copy image to images directory
        images_dir = "images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        dest_path = os.path.join(images_dir, filename)

        # Handle duplicate filenames
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            filename = f"{base}_{counter}{ext}"
            dest_path = os.path.join(images_dir, filename)
            counter += 1

        # Copy file
        shutil.copy2(file_path, dest_path)

        # Get mouse position for node placement
        mouse_pos = get_mouse_position_in_editor()

        # Create image node at mouse position
        width = 300
        height = 300

        # Import and call with position override
        create_image_node_at_position(label, dest_path, width, height, mouse_pos)

        print(f"  ✓ Image added: {label}")
        show_success_notification(f"Image added: {label}")

    except Exception as e:
        print(f"  ✗ Error adding image: {e}")
        import traceback
        traceback.print_exc()


def handle_audio_drop(file_path):
    """Handle dropped audio file"""
    try:
        from nodes.audio import create_audio_node
        import shutil

        filename = os.path.basename(file_path)
        label = os.path.splitext(filename)[0]

        # Copy audio to audio directory
        audio_dir = "audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        dest_path = os.path.join(audio_dir, filename)

        # Handle duplicate filenames
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            filename = f"{base}_{counter}{ext}"
            dest_path = os.path.join(audio_dir, filename)
            counter += 1

        # Copy file
        shutil.copy2(file_path, dest_path)

        # Get mouse position for node placement
        mouse_pos = get_mouse_position_in_editor()

        # Create audio node at mouse position
        create_audio_node_at_position(label, dest_path, mouse_pos)

        print(f"  ✓ Audio added: {label}")
        show_success_notification(f"Audio added: {label}")

    except Exception as e:
        print(f"  ✗ Error adding audio: {e}")
        import traceback
        traceback.print_exc()


def handle_script_drop(file_path):
    """Handle dropped Python script"""
    try:
        from scripts.script_manager import save_script
        from scripts.script_nodes import add_script_node

        filename = os.path.basename(file_path)
        script_name = os.path.splitext(filename)[0]

        # Read script content
        with open(file_path, 'r', encoding='utf-8') as f:
            script_code = f.read()

        # Save script
        save_script(script_name, script_code)

        # Add script node at mouse position
        mouse_pos = get_mouse_position_in_editor()
        add_script_node_at_position(script_name, mouse_pos)

        print(f"  ✓ Script added: {script_name}.py")
        show_success_notification(f"Script added: {script_name}.py")

    except Exception as e:
        print(f"  ✗ Error adding script: {e}")


def handle_text_drop(file_path):
    """Handle dropped text/markdown file"""
    try:
        from nodes.text import create_text_node

        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]

        # Read text content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create text node at mouse position
        mouse_pos = get_mouse_position_in_editor()
        create_text_node_at_position(title, content, mouse_pos)

        print(f"  ✓ Text note added: {title}")
        show_success_notification(f"Note added: {title}")

    except Exception as e:
        print(f"  ✗ Error adding text: {e}")


def get_mouse_position_in_editor():
    """Get mouse position relative to node editor"""
    try:
        # Get mouse position
        mouse_pos = dpg.get_mouse_pos(local=False)

        # Get node editor position and offset
        if dpg.does_item_exist(app_state.node_editor):
            # Get the canvas position/offset
            # This returns the pan offset of the node editor
            canvas_offset = dpg.get_item_state(app_state.node_editor).get("pos", [0, 0])

            # Adjust mouse position by canvas offset
            # Note: You may need to adjust this based on your window position
            adjusted_x = mouse_pos[0] - canvas_offset[0]
            adjusted_y = mouse_pos[1] - canvas_offset[1]

            return [adjusted_x, adjusted_y]

        # Fallback to mouse position
        return list(mouse_pos)

    except Exception as e:
        print(f"Error getting mouse position: {e}")
        # Return a default position near top-left
        return [100, 100]


def create_image_node_at_position(label, image_path, width, height, pos):
    """Create image node at specific position"""
    import dearpygui.dearpygui as dpg
    import os
    from config import app_state

    try:
        import numpy as np
        from PIL import Image

        new_node_id = dpg.generate_uuid()

        # Load and register the image texture
        pil_image = Image.open(image_path)
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')

        # Get original dimensions
        orig_width, orig_height = pil_image.size

        # Resize if needed
        if width != orig_width or height != orig_height:
            pil_image = pil_image.resize((width, height), Image.LANCZOS)

        # Convert to numpy array and normalize
        image_array = np.array(pil_image).astype('f') / 255.0
        texture_data = image_array.flatten()

        # Register texture
        texture_tag = f"texture_{new_node_id}"
        with dpg.texture_registry():
            dpg.add_raw_texture(
                width=width,
                height=height,
                default_value=texture_data,
                format=dpg.mvFormat_Float_rgba,
                tag=texture_tag
            )

        # Store image data
        image_key = f"image_{new_node_id}"
        if not hasattr(app_state, 'image_nodes'):
            app_state.image_nodes = {}

        app_state.image_nodes[image_key] = {
            "id": new_node_id,
            "label": label,
            "path": image_path,
            "width": width,
            "height": height,
            "texture_tag": texture_tag,
            "author": app_state.current_user
        }

        # Create the node at specified position
        preview_label = label[:25] + "..." if len(label) > 25 else label

        with dpg.node(label=f"🖼️ {preview_label}", pos=pos,
                      parent=app_state.node_editor, tag=new_node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text("🖼️ " + label, color=(255, 200, 100))

                    from nodes.image import show_image_viewer, edit_image_node, delete_image_node

                    dpg.add_button(label="🔍", width=30,
                                   callback=lambda: show_image_viewer(image_key),
                                   tag=f"view_btn_{new_node_id}")
                    dpg.add_button(label="✏️", width=30,
                                   callback=lambda: edit_image_node(image_key))
                    dpg.add_button(label="❌", width=30,
                                   callback=lambda: delete_image_node(new_node_id, image_key))

                dpg.add_separator()
                dpg.add_image(texture_tag, width=width, height=height)
                dpg.add_separator()

                dpg.add_text(f"By: {app_state.current_user}",
                             color=app_state.current_user_color)
                dpg.add_text(f"Size: {width}x{height}px", color=(150, 150, 150))

        with dpg.tooltip(f"view_btn_{new_node_id}"):
            dpg.add_text("Click to view full size")

        return new_node_id

    except Exception as e:
        print(f"Error creating image node at position: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_audio_node_at_position(label, audio_path, pos):
    """Create audio node at specific position"""
    import dearpygui.dearpygui as dpg
    import os
    from config import app_state

    try:
        new_node_id = dpg.generate_uuid()

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

        # Create minimalistic node at specified position
        with dpg.node(label=f"{display_label}", pos=pos,
                      parent=app_state.node_editor, tag=new_node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text("🔊", color=(100, 255, 100),
                                 tag=f"play_icon_{new_node_id}")

                    from nodes.audio import toggle_audio, edit_audio_node, delete_audio_node

                    dpg.add_button(label="▶️", width=60, height=20,
                                   callback=lambda: toggle_audio(audio_key),
                                   tag=f"play_btn_{new_node_id}")
                    dpg.add_button(label="✏️", width=25, height=20,
                                   callback=lambda: edit_audio_node(audio_key))
                    dpg.add_button(label="❌", width=25, height=20,
                                   callback=lambda: delete_audio_node(new_node_id, audio_key))

        return new_node_id

    except Exception as e:
        print(f"Error creating audio node at position: {e}")
        return None


def add_script_node_at_position(script_name, pos):
    """Add script node at specific position"""
    import dearpygui.dearpygui as dpg
    from config import app_state
    from scripts.script_manager import run_script, stop_script

    try:
        if script_name in app_state.script_nodes:
            print(f"Script node {script_name} already exists")
            return app_state.script_nodes[script_name]

        new_node_id = dpg.generate_uuid()
        app_state.script_nodes[script_name] = new_node_id

        with dpg.node(label=f"🐍 {script_name}", pos=pos,
                      parent=app_state.node_editor, tag=new_node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text(f"📜 {script_name}.py", color=(100, 255, 100))

                    from scripts.script_nodes import delete_script_node, edit_script_callback

                    dpg.add_button(label="❌", width=30,
                                   callback=lambda: delete_script_node(new_node_id, script_name))

                dpg.add_text(f"By: {app_state.current_user}", color=app_state.current_user_color)

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Run", width=70,
                                   callback=lambda: run_script(script_name))
                    dpg.add_button(label="Edit", width=70,
                                   callback=lambda: edit_script_callback(script_name))
                    dpg.add_button(label="Stop", width=70,
                                   callback=lambda: stop_script(script_name))

        return new_node_id

    except Exception as e:
        print(f"Error creating script node at position: {e}")
        return None


def create_text_node_at_position(title, content, pos):
    """Create text node at specific position"""
    import dearpygui.dearpygui as dpg
    import os
    from config import app_state

    try:
        new_node_id = dpg.generate_uuid()

        # Save content to markdown file
        notes_dir = "notes"
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)

        filename = f"{title.replace(' ', '_')}_{new_node_id}.md"
        filepath = os.path.join(notes_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        text_key = f"text_{new_node_id}"
        app_state.text_nodes[text_key] = {
            "id": new_node_id,
            "title": title,
            "filepath": filepath,
            "author": app_state.current_user
        }

        # Create preview
        preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content.replace('\n', ' ')

        with dpg.node(label=f"📝 {title}", pos=pos,
                      parent=app_state.node_editor, tag=new_node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text("📝 Note", color=(255, 255, 100))

                    from nodes.text import show_full_note, edit_text_node, delete_text_node

                    dpg.add_button(label="📄", width=30,
                                   callback=lambda: show_full_note(text_key),
                                   tag=f"view_btn_{new_node_id}")
                    dpg.add_button(label="✏️", width=30,
                                   callback=lambda: edit_text_node(text_key))
                    dpg.add_button(label="❌", width=30,
                                   callback=lambda: delete_text_node(new_node_id, text_key))

                dpg.add_separator()
                dpg.add_text(title, color=(200, 200, 255), wrap=250)
                dpg.add_separator()
                dpg.add_text(preview, tag=f"text_preview_{new_node_id}",
                             color=(180, 180, 180), wrap=250)
                dpg.add_separator()
                dpg.add_text(f"By: {app_state.current_user}",
                             color=app_state.current_user_color)

        with dpg.tooltip(f"view_btn_{new_node_id}"):
            dpg.add_text("Click to view full note")

        return new_node_id

    except Exception as e:
        print(f"Error creating text node at position: {e}")
        return None


def show_success_notification(message):
    """Show a temporary success notification"""
    notif_id = "drop_success_notif"

    if dpg.does_item_exist(notif_id):
        dpg.delete_item(notif_id)

    with dpg.window(label="✓ File Added", tag=notif_id,
                    width=300, height=100, pos=[500, 50],
                    no_resize=True, no_move=True, no_collapse=True,
                    modal=False, popup=True):
        dpg.add_text(message, color=(100, 255, 100))
        dpg.add_separator()
        dpg.add_text("Drag more files or close this", color=(150, 150, 150))

    # Auto-close after 3 seconds
    dpg.set_frame_callback(90, lambda: dpg.delete_item(notif_id) if dpg.does_item_exist(notif_id) else None)


def show_unsupported_file_notification(file_path):
    """Show notification for unsupported file types"""
    notif_id = "drop_unsupported_notif"

    if dpg.does_item_exist(notif_id):
        dpg.delete_item(notif_id)

    filename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1]

    with dpg.window(label="⚠️ Unsupported File", tag=notif_id,
                    width=400, height=180, pos=[450, 50],
                    no_resize=True, modal=True):
        dpg.add_text(f"Cannot add file: {filename}", color=(255, 200, 100), wrap=380)
        dpg.add_separator()
        dpg.add_text(f"File type '{ext}' is not supported", wrap=380)
        dpg.add_spacer(height=10)
        dpg.add_text("Supported types:", color=(150, 200, 255))
        dpg.add_text("• Images: .png, .jpg, .jpeg, .bmp, .gif", wrap=380)
        dpg.add_text("• Audio: .mp3, .wav, .ogg, .flac, .m4a", wrap=380)
        dpg.add_text("• Scripts: .py", wrap=380)
        dpg.add_text("• Text: .txt, .md, .markdown", wrap=380)
        dpg.add_separator()
        dpg.add_button(label="OK", width=150, callback=lambda: dpg.delete_item(notif_id))