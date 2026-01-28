# ===========================================
# FILE: nodes/image.py (SIMPLIFIED AUTO-ADD)
# ===========================================

import dearpygui.dearpygui as dpg
import random
import os
from config import app_state

# Directory for storing images
IMAGES_DIR = "images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)


def show_add_image_dialog():
    """Show file dialog directly - image is added automatically after selection"""
    # Clean up any existing file dialog
    if dpg.does_item_exist("image_file_dialog"):
        dpg.delete_item("image_file_dialog")

    # Show file dialog directly
    with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=image_file_selected_auto,
            tag="image_file_dialog",
            width=700,
            height=400,
            modal=True,
            default_path=os.path.expanduser("~")
    ):
        dpg.add_file_extension(".*")
        dpg.add_file_extension(".png", color=(0, 255, 0, 255))
        dpg.add_file_extension(".jpg", color=(255, 255, 0, 255))
        dpg.add_file_extension(".jpeg", color=(255, 255, 0, 255))
        dpg.add_file_extension(".bmp", color=(0, 255, 255, 255))


def image_file_selected_auto(sender, app_data):
    """Handle image file selection - automatically create node"""
    if not app_data["selections"]:
        return

    filepath = list(app_data["selections"].values())[0]
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return

    # Use filename (without extension) as default label
    label = os.path.splitext(filename)[0]

    # Default dimensions
    width = 300
    height = 300

    # Copy image to images directory
    import shutil
    dest_path = os.path.join(IMAGES_DIR, filename)

    # Handle duplicate filenames
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(dest_path):
        filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(IMAGES_DIR, filename)
        counter += 1

    try:
        shutil.copy2(filepath, dest_path)
        create_image_node(label, dest_path, width, height)
        print(f"✓ Image added: {label}")
    except Exception as e:
        print(f"Error adding image: {e}")


def create_image_node(label, image_path, width, height):
    """Create an image node on the board"""
    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()

    # Load and register the image texture
    try:
        import numpy as np
        from PIL import Image

        # Load image with PIL
        pil_image = Image.open(image_path)

        # Convert to RGBA if necessary
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')

        # Get original dimensions
        orig_width, orig_height = pil_image.size

        # Resize if needed
        if width != orig_width or height != orig_height:
            pil_image = pil_image.resize((width, height), Image.LANCZOS)

        # Convert to numpy array and normalize
        image_array = np.array(pil_image).astype('f') / 255.0

        # Flatten for DearPyGUI
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

        # Create the node
        preview_label = label[:25] + "..." if len(label) > 25 else label

        with dpg.node(label=f"🖼️ {preview_label}", pos=pos,
                      parent=app_state.node_editor, tag=new_node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text("🖼️ " + label, color=(255, 200, 100))
                    dpg.add_button(label="🔍", width=30,
                                   callback=lambda: show_image_viewer(image_key),
                                   tag=f"view_btn_{new_node_id}")
                    dpg.add_button(label="✏️", width=30,
                                   callback=lambda: edit_image_node(image_key))
                    dpg.add_button(label="❌", width=30,
                                   callback=lambda: delete_image_node(new_node_id, image_key))

                dpg.add_separator()

                # Display the image
                dpg.add_image(texture_tag, width=width, height=height)

                dpg.add_separator()
                dpg.add_text(f"By: {app_state.current_user}",
                             color=app_state.current_user_color)
                dpg.add_text(f"Size: {width}x{height}px", color=(150, 150, 150))

        # Add tooltip
        with dpg.tooltip(f"view_btn_{new_node_id}"):
            dpg.add_text("Click to view full size")

    except Exception as e:
        print(f"Error creating image node: {e}")
        import traceback
        traceback.print_exc()


def show_image_viewer(image_key):
    """Show full-size image viewer"""
    if not hasattr(app_state, 'image_nodes') or image_key not in app_state.image_nodes:
        return

    image_data = app_state.image_nodes[image_key]
    viewer_id = f"viewer_{image_key}"

    if dpg.does_item_exist(viewer_id):
        dpg.delete_item(viewer_id)

    # Calculate window size (with max limits)
    img_width = min(image_data["width"], 1000)
    img_height = min(image_data["height"], 700)
    window_width = img_width + 40
    window_height = img_height + 120

    with dpg.window(label=f"View: {image_data['label']}", tag=viewer_id,
                    width=window_width, height=window_height,
                    pos=[100, 100], modal=False):

        with dpg.group(horizontal=True):
            dpg.add_text("🖼️ " + image_data['label'], color=(255, 200, 100))

        dpg.add_text(f"File: {os.path.basename(image_data['path'])}",
                     color=(150, 150, 150))
        dpg.add_text(f"Original size: {image_data['width']}x{image_data['height']}px",
                     color=(150, 150, 150))

        dpg.add_separator()

        # Show image at actual size (or scaled down if too large)
        dpg.add_image(image_data["texture_tag"],
                      width=img_width, height=img_height)

        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Close", width=100,
                           callback=lambda: dpg.delete_item(viewer_id))


def edit_image_node(image_key):
    """Edit an existing image node"""
    if not hasattr(app_state, 'image_nodes') or image_key not in app_state.image_nodes:
        return

    image_data = app_state.image_nodes[image_key]
    editor_id = f"edit_image_{image_key}"

    if dpg.does_item_exist(editor_id):
        dpg.delete_item(editor_id)

    with dpg.window(label=f"Edit Image: {image_data['label']}", tag=editor_id,
                    modal=True, width=450, height=350, pos=[225, 150]):

        dpg.add_text("Edit image properties:")
        dpg.add_separator()

        dpg.add_text("Label:")
        dpg.add_input_text(tag=f"edit_label_{image_key}", width=420,
                           default_value=image_data['label'])

        dpg.add_separator()
        dpg.add_text("Display Size:")

        dpg.add_text("Width (pixels):")
        dpg.add_slider_int(tag=f"edit_width_{image_key}", width=420,
                           default_value=image_data['width'],
                           min_value=100, max_value=800)

        dpg.add_text("Height (pixels):")
        dpg.add_slider_int(tag=f"edit_height_{image_key}", width=420,
                           default_value=image_data['height'],
                           min_value=100, max_value=800)

        dpg.add_separator()
        dpg.add_text("", tag=f"edit_message_{image_key}")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", width=150,
                           callback=lambda: save_image_edit(image_key, editor_id))
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(editor_id))


def save_image_edit(image_key, editor_id):
    """Save changes to image node"""
    if not hasattr(app_state, 'image_nodes') or image_key not in app_state.image_nodes:
        return

    new_label = dpg.get_value(f"edit_label_{image_key}").strip()
    new_width = dpg.get_value(f"edit_width_{image_key}")
    new_height = dpg.get_value(f"edit_height_{image_key}")

    if not new_label:
        dpg.set_value(f"edit_message_{image_key}", "Please enter a label!")
        dpg.configure_item(f"edit_message_{image_key}", color=(255, 0, 0))
        return

    image_data = app_state.image_nodes[image_key]
    node_id = image_data["id"]

    # Update stored data
    image_data["label"] = new_label
    image_data["width"] = new_width
    image_data["height"] = new_height

    # Recreate the node with new properties
    if dpg.does_item_exist(node_id):
        # Get current position
        pos = dpg.get_item_pos(node_id)

        # Delete old node
        dpg.delete_item(node_id)

        # Create new node with same ID at same position
        create_image_node_at_position(image_data, pos)

    dpg.delete_item(editor_id)


def create_image_node_at_position(image_data, pos):
    """Helper to recreate image node at specific position"""
    node_id = image_data["id"]
    texture_tag = image_data["texture_tag"]
    label = image_data["label"]
    width = image_data["width"]
    height = image_data["height"]

    # Reload and resize texture
    try:
        import numpy as np
        from PIL import Image

        pil_image = Image.open(image_data["path"])
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        pil_image = pil_image.resize((width, height), Image.LANCZOS)
        image_array = np.array(pil_image).astype('f') / 255.0
        texture_data = image_array.flatten()

        # Delete old texture and create new one
        if dpg.does_item_exist(texture_tag):
            dpg.delete_item(texture_tag)

        with dpg.texture_registry():
            dpg.add_raw_texture(
                width=width,
                height=height,
                default_value=texture_data,
                format=dpg.mvFormat_Float_rgba,
                tag=texture_tag
            )

        # Recreate node
        preview_label = label[:25] + "..." if len(label) > 25 else label
        image_key = f"image_{node_id}"

        with dpg.node(label=f"🖼️ {preview_label}", pos=pos,
                      parent=app_state.node_editor, tag=node_id):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                with dpg.group(horizontal=True):
                    dpg.add_text("🖼️ " + label, color=(255, 200, 100))
                    dpg.add_button(label="🔍", width=30,
                                   callback=lambda: show_image_viewer(image_key),
                                   tag=f"view_btn_{node_id}")
                    dpg.add_button(label="✏️", width=30,
                                   callback=lambda: edit_image_node(image_key))
                    dpg.add_button(label="❌", width=30,
                                   callback=lambda: delete_image_node(node_id, image_key))

                dpg.add_separator()
                dpg.add_image(texture_tag, width=width, height=height)
                dpg.add_separator()

                dpg.add_text(f"By: {image_data['author']}",
                             color=app_state.current_user_color)
                dpg.add_text(f"Size: {width}x{height}px", color=(150, 150, 150))

        with dpg.tooltip(f"view_btn_{node_id}"):
            dpg.add_text("Click to view full size")

    except Exception as e:
        print(f"Error recreating image node: {e}")


def delete_image_node(node_id, image_key):
    """Delete an image node"""
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    if hasattr(app_state, 'image_nodes') and image_key in app_state.image_nodes:
        # Delete texture
        texture_tag = app_state.image_nodes[image_key].get("texture_tag")
        if texture_tag and dpg.does_item_exist(texture_tag):
            dpg.delete_item(texture_tag)

        del app_state.image_nodes[image_key]