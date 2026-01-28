# ===========================================
# FILE: nodes/highlight.py (REWORKED)
# ===========================================

import dearpygui.dearpygui as dpg
import random
from config import app_state


def show_create_highlight_dialog():
    """Show dialog to create highlight box with presets"""
    dialog_id = "create_highlight_dialog"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="Create Highlight Box", tag=dialog_id, modal=True,
                    width=500, height=450, pos=[225, 125]):
        dpg.add_text("📦 Add an organizational highlight box", color=(150, 200, 255))
        dpg.add_separator()

        # Label
        dpg.add_text("Label:")
        dpg.add_input_text(tag="highlight_label", width=470, default_value="Project Area")

        dpg.add_separator()

        # Quick presets
        dpg.add_text("Quick Presets:", color=(200, 200, 100))
        with dpg.group(horizontal=True):
            dpg.add_button(label="📋 Small", width=90,
                           callback=lambda: apply_preset("small"))
            dpg.add_button(label="📦 Medium", width=90,
                           callback=lambda: apply_preset("medium"))
            dpg.add_button(label="🎯 Large", width=90,
                           callback=lambda: apply_preset("large"))
            dpg.add_button(label="📊 Wide", width=90,
                           callback=lambda: apply_preset("wide"))
            dpg.add_button(label="📏 Tall", width=90,
                           callback=lambda: apply_preset("tall"))

        dpg.add_separator()

        # Size controls
        dpg.add_text("Custom Size:")
        dpg.add_text("Width:")
        dpg.add_slider_int(tag="highlight_width", width=450,
                           default_value=400, min_value=200, max_value=1000,
                           format="%d px")

        dpg.add_text("Height:")
        dpg.add_slider_int(tag="highlight_height", width=450,
                           default_value=300, min_value=150, max_value=800,
                           format="%d px")

        dpg.add_separator()

        # Color presets
        dpg.add_text("Color Presets:", color=(200, 200, 100))
        with dpg.group(horizontal=True):
            dpg.add_button(label="🔵 Blue", width=70,
                           callback=lambda: set_color_preset([100, 150, 255, 200]))
            dpg.add_button(label="🟢 Green", width=70,
                           callback=lambda: set_color_preset([100, 255, 150, 200]))
            dpg.add_button(label="🔴 Red", width=70,
                           callback=lambda: set_color_preset([255, 100, 100, 200]))
            dpg.add_button(label="🟡 Yellow", width=70,
                           callback=lambda: set_color_preset([255, 255, 100, 200]))
            dpg.add_button(label="🟣 Purple", width=70,
                           callback=lambda: set_color_preset([200, 100, 255, 200]))
            dpg.add_button(label="🟠 Orange", width=70,
                           callback=lambda: set_color_preset([255, 165, 0, 200]))

        dpg.add_separator()

        # Custom color
        dpg.add_text("Custom Color:")
        dpg.add_color_edit(tag="highlight_color_picker",
                           default_value=[100, 150, 255, 200],
                           alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                           width=450)

        dpg.add_text("💡 Other nodes will appear on top of this box",
                     color=(150, 150, 150))

        dpg.add_separator()
        dpg.add_text("", tag="highlight_create_message")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create", width=220, height=35,
                           callback=create_highlight_from_dialog)
            dpg.add_button(label="Cancel", width=220, height=35,
                           callback=lambda: dpg.delete_item(dialog_id))


def apply_preset(preset_name):
    """Apply size preset"""
    presets = {
        "small": (300, 200),
        "medium": (400, 300),
        "large": (600, 450),
        "wide": (800, 300),
        "tall": (350, 600)
    }

    if preset_name in presets:
        width, height = presets[preset_name]
        dpg.set_value("highlight_width", width)
        dpg.set_value("highlight_height", height)


def set_color_preset(color):
    """Set color picker to preset"""
    if dpg.does_item_exist("highlight_color_picker"):
        dpg.set_value("highlight_color_picker", color)


def create_highlight_from_dialog():
    """Create highlight box from dialog inputs"""
    label = dpg.get_value("highlight_label")
    width = dpg.get_value("highlight_width")
    height = dpg.get_value("highlight_height")
    color = dpg.get_value("highlight_color_picker")

    if not label or not label.strip():
        dpg.set_value("highlight_create_message", "Please enter a label!")
        dpg.configure_item("highlight_create_message", color=(255, 0, 0))
        return

    result = create_highlight_box(label.strip(), width, height, color)

    if result:
        dpg.delete_item("create_highlight_dialog")
    else:
        dpg.set_value("highlight_create_message", "Failed to create highlight box!")
        dpg.configure_item("highlight_create_message", color=(255, 0, 0))


def create_highlight_box(label, width, height, color):
    """Create a highlight box node with improved design"""

    if not app_state.node_editor:
        print("ERROR: node_editor is None! Cannot create highlight box.")
        return None

    if not dpg.does_item_exist(app_state.node_editor):
        print(f"ERROR: node_editor {app_state.node_editor} doesn't exist!")
        return None

    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()
    app_state.highlight_boxes[label] = new_node_id

    # Store properties
    if not hasattr(app_state, 'highlight_properties'):
        app_state.highlight_properties = {}

    app_state.highlight_properties[label] = {
        "width": width,
        "height": height,
        "color": list(color) if isinstance(color, (list, tuple)) else [255, 255, 0, 50],
        "locked": False,
        "locked_nodes": []
    }

    def delete_callback():
        if dpg.does_item_exist(new_node_id):
            dpg.delete_item(new_node_id)
        if label in app_state.highlight_boxes:
            del app_state.highlight_boxes[label]
        if hasattr(app_state, 'highlight_properties') and label in app_state.highlight_properties:
            del app_state.highlight_properties[label]

    def edit_callback():
        show_edit_highlight_dialog(label, new_node_id)

    def toggle_lock():
        """Toggle lock state for nodes inside the box"""
        props = app_state.highlight_properties[label]

        if props["locked"]:
            # Unlock - clear the locked nodes list
            props["locked"] = False
            props["locked_nodes"] = []
            print(f"🔓 Unlocked highlight box: {label}")
        else:
            # Lock - capture all nodes currently inside the box
            props["locked"] = True
            props["locked_nodes"] = capture_nodes_inside_box(new_node_id, width, height)
            print(f"🔒 Locked highlight box: {label} with {len(props['locked_nodes'])} nodes")

        # Update the lock button appearance
        update_lock_button(new_node_id, label)

    # Shorter label for node title
    display_label = label[:20] + "..." if len(label) > 20 else label

    with dpg.node(label=f"📦 {display_label}", pos=pos,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            # Control bar
            with dpg.group(horizontal=True):
                dpg.add_text("📦", color=(255, 255, 100))
                dpg.add_text(label, color=(220, 220, 255), wrap=width - 130)
                dpg.add_button(label="🔓", width=30, height=25,
                               callback=toggle_lock,
                               tag=f"lock_btn_{new_node_id}")
                dpg.add_button(label="✏️", width=30, height=25,
                               callback=edit_callback)
                dpg.add_button(label="❌", width=30, height=25,
                               callback=delete_callback)

            dpg.add_separator()

            # Main highlight area with rounded corners and gradient
            with dpg.drawlist(width=width, height=height, tag=f"drawlist_{new_node_id}"):
                # Background with gradient effect
                fill_color = (int(color[0]), int(color[1]), int(color[2]), int(color[3] * 0.3))
                border_color = (int(color[0]), int(color[1]), int(color[2]), int(color[3]))

                # Main rectangle with rounded corners
                dpg.draw_rectangle(
                    (0, 0), (width, height),
                    fill=fill_color,
                    color=border_color,
                    rounding=8,
                    thickness=2
                )

                # Corner accents (decorative)
                accent_size = 20
                dpg.draw_line((0, 0), (accent_size, 0),
                              color=border_color, thickness=3)
                dpg.draw_line((0, 0), (0, accent_size),
                              color=border_color, thickness=3)

                dpg.draw_line((width - accent_size, 0), (width, 0),
                              color=border_color, thickness=3)
                dpg.draw_line((width, 0), (width, accent_size),
                              color=border_color, thickness=3)

                # Label in center with shadow effect
                text_x = width // 2 - len(label) * 4
                text_y = height // 2 - 8

                # Shadow
                dpg.draw_text((text_x + 1, text_y + 1), f"📦 {label}",
                              color=(0, 0, 0, 80), size=16)
                # Main text
                dpg.draw_text((text_x, text_y), f"📦 {label}",
                              color=(255, 255, 255, 200), size=16)

                # Size indicator
                size_text = f"{width}×{height}px"
                dpg.draw_text((10, height - 25), size_text,
                              color=(255, 255, 255, 150), size=11)

                # Lock indicator
                if app_state.highlight_properties[label]["locked"]:
                    num_locked = len(app_state.highlight_properties[label]["locked_nodes"])
                    lock_text = f"🔒 {num_locked} nodes locked"
                    dpg.draw_text((width - 140, height - 25), lock_text,
                                  color=(255, 200, 100, 200), size=11)

            dpg.add_separator()
            dpg.add_text(f"By: {app_state.current_user}",
                         color=app_state.current_user_color)

    print(f"Successfully created highlight box: {label}")
    return new_node_id


def show_edit_highlight_dialog(label, node_id):
    """Show dialog to edit an existing highlight box"""
    dialog_id = f"edit_highlight_{node_id}"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    if not hasattr(app_state, 'highlight_properties') or label not in app_state.highlight_properties:
        return

    props = app_state.highlight_properties[label]

    with dpg.window(label=f"Edit: {label}", tag=dialog_id, modal=True,
                    width=500, height=400, pos=[225, 150]):

        dpg.add_text(f"✏️ Edit Highlight Box", color=(150, 200, 255))
        dpg.add_separator()

        # New label
        dpg.add_text("Label:")
        dpg.add_input_text(tag=f"edit_label_{node_id}", width=470,
                           default_value=label)

        dpg.add_separator()

        # Size
        dpg.add_text("Width:")
        dpg.add_slider_int(tag=f"edit_width_{node_id}", width=450,
                           default_value=props["width"],
                           min_value=200, max_value=1000,
                           format="%d px")

        dpg.add_text("Height:")
        dpg.add_slider_int(tag=f"edit_height_{node_id}", width=450,
                           default_value=props["height"],
                           min_value=150, max_value=800,
                           format="%d px")

        dpg.add_separator()

        # Color
        dpg.add_text("Color:")
        dpg.add_color_edit(tag=f"edit_color_{node_id}",
                           default_value=props["color"],
                           alpha_preview=dpg.mvColorEdit_AlphaPreviewHalf,
                           width=450)

        dpg.add_separator()
        dpg.add_text("", tag=f"edit_message_{node_id}")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", width=220, height=35,
                           callback=lambda: save_highlight_edit(label, node_id, dialog_id))
            dpg.add_button(label="Cancel", width=220, height=35,
                           callback=lambda: dpg.delete_item(dialog_id))


def save_highlight_edit(old_label, node_id, dialog_id):
    """Save edits to highlight box"""
    new_label = dpg.get_value(f"edit_label_{node_id}").strip()
    new_width = dpg.get_value(f"edit_width_{node_id}")
    new_height = dpg.get_value(f"edit_height_{node_id}")
    new_color = dpg.get_value(f"edit_color_{node_id}")

    if not new_label:
        dpg.set_value(f"edit_message_{node_id}", "Please enter a label!")
        dpg.configure_item(f"edit_message_{node_id}", color=(255, 0, 0))
        return

    # Update stored data
    if old_label in app_state.highlight_boxes:
        del app_state.highlight_boxes[old_label]
    app_state.highlight_boxes[new_label] = node_id

    if hasattr(app_state, 'highlight_properties'):
        if old_label in app_state.highlight_properties:
            del app_state.highlight_properties[old_label]
        app_state.highlight_properties[new_label] = {
            "width": new_width,
            "height": new_height,
            "color": list(new_color)
        }

    # Recreate the node
    if dpg.does_item_exist(node_id):
        pos = dpg.get_item_pos(node_id)
        dpg.delete_item(node_id)

        # Recreate at same position
        recreate_highlight_box(new_label, node_id, pos, new_width, new_height, new_color)

    dpg.delete_item(dialog_id)


def recreate_highlight_box(label, node_id, pos, width, height, color):
    """Recreate highlight box with new properties"""

    def delete_callback():
        if dpg.does_item_exist(node_id):
            dpg.delete_item(node_id)
        if label in app_state.highlight_boxes:
            del app_state.highlight_boxes[label]
        if hasattr(app_state, 'highlight_properties') and label in app_state.highlight_properties:
            del app_state.highlight_properties[label]

    def edit_callback():
        show_edit_highlight_dialog(label, node_id)

    def toggle_lock():
        """Toggle lock state for nodes inside the box"""
        props = app_state.highlight_properties[label]

        if props["locked"]:
            # Unlock - clear the locked nodes list
            props["locked"] = False
            props["locked_nodes"] = []
            print(f"🔓 Unlocked highlight box: {label}")
        else:
            # Lock - capture all nodes currently inside the box
            props["locked"] = True
            props["locked_nodes"] = capture_nodes_inside_box(node_id, width, height)
            print(f"🔒 Locked highlight box: {label} with {len(props['locked_nodes'])} nodes")

        # Update the lock button appearance
        update_lock_button(node_id, label)

    display_label = label[:20] + "..." if len(label) > 20 else label

    with dpg.node(label=f"📦 {display_label}", pos=pos,
                  parent=app_state.node_editor, tag=node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.group(horizontal=True):
                dpg.add_text("📦", color=(255, 255, 100))
                dpg.add_text(label, color=(220, 220, 255), wrap=width - 130)
                dpg.add_button(label="🔓", width=30, height=25,
                               callback=toggle_lock,
                               tag=f"lock_btn_{node_id}")
                dpg.add_button(label="✏️", width=30, height=25,
                               callback=edit_callback)
                dpg.add_button(label="❌", width=30, height=25,
                               callback=delete_callback)

            dpg.add_separator()

            with dpg.drawlist(width=width, height=height, tag=f"drawlist_{node_id}"):
                fill_color = (int(color[0]), int(color[1]), int(color[2]), int(color[3] * 0.3))
                border_color = (int(color[0]), int(color[1]), int(color[2]), int(color[3]))

                dpg.draw_rectangle(
                    (0, 0), (width, height),
                    fill=fill_color,
                    color=border_color,
                    rounding=8,
                    thickness=2
                )

                accent_size = 20
                dpg.draw_line((0, 0), (accent_size, 0),
                              color=border_color, thickness=3)
                dpg.draw_line((0, 0), (0, accent_size),
                              color=border_color, thickness=3)

                dpg.draw_line((width - accent_size, 0), (width, 0),
                              color=border_color, thickness=3)
                dpg.draw_line((width, 0), (width, accent_size),
                              color=border_color, thickness=3)

                text_x = width // 2 - len(label) * 4
                text_y = height // 2 - 8

                dpg.draw_text((text_x + 1, text_y + 1), f"📦 {label}",
                              color=(0, 0, 0, 80), size=16)
                dpg.draw_text((text_x, text_y), f"📦 {label}",
                              color=(255, 255, 255, 200), size=16)

                size_text = f"{width}×{height}px"
                dpg.draw_text((10, height - 25), size_text,
                              color=(255, 255, 255, 150), size=11)

                # Lock indicator
                if app_state.highlight_properties[label]["locked"]:
                    num_locked = len(app_state.highlight_properties[label]["locked_nodes"])
                    lock_text = f"🔒 {num_locked} nodes locked"
                    dpg.draw_text((width - 140, height - 25), lock_text,
                                  color=(255, 200, 100, 200), size=11)

            dpg.add_separator()
            dpg.add_text(f"By: {app_state.current_user}",
                         color=app_state.current_user_color)

    # Update lock button state
    update_lock_button(node_id, label)


def delete_highlight_box(node_id, label):
    """Delete a highlight box"""
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    if label in app_state.highlight_boxes:
        del app_state.highlight_boxes[label]

    if hasattr(app_state, 'highlight_properties') and label in app_state.highlight_properties:
        del app_state.highlight_properties[label]


def capture_nodes_inside_box(box_node_id, box_width, box_height):
    """Capture all node IDs that are currently inside the highlight box"""
    if not dpg.does_item_exist(box_node_id):
        return []

    box_pos = dpg.get_item_pos(box_node_id)
    box_x, box_y = box_pos

    # Define the box boundaries (with some padding for the node header)
    box_left = box_x
    box_right = box_x + box_width
    box_top = box_y + 40  # Account for node header
    box_bottom = box_y + box_height + 40

    locked_nodes = []

    # Check all node types
    all_node_dicts = [
        app_state.node_chats,
        app_state.script_nodes,
        app_state.highlight_boxes,
        app_state.text_nodes,
    ]

    if hasattr(app_state, 'image_nodes'):
        all_node_dicts.append({k: v["id"] for k, v in app_state.image_nodes.items()})

    if hasattr(app_state, 'audio_nodes'):
        all_node_dicts.append({k: v["id"] for k, v in app_state.audio_nodes.items()})

    for node_dict in all_node_dicts:
        for key, node_id in node_dict.items():
            # Skip the box itself
            if node_id == box_node_id:
                continue

            if dpg.does_item_exist(node_id):
                node_pos = dpg.get_item_pos(node_id)
                node_x, node_y = node_pos

                # Check if node center is inside the box
                if (box_left <= node_x <= box_right and
                        box_top <= node_y <= box_bottom):
                    locked_nodes.append({
                        "id": node_id,
                        "offset_x": node_x - box_x,
                        "offset_y": node_y - box_y
                    })

    return locked_nodes


def update_lock_button(box_node_id, label):
    """Update the lock button appearance based on lock state"""
    lock_btn_id = f"lock_btn_{box_node_id}"

    if not dpg.does_item_exist(lock_btn_id):
        return

    props = app_state.highlight_properties.get(label, {})
    is_locked = props.get("locked", False)

    if is_locked:
        dpg.configure_item(lock_btn_id, label="🔒")
    else:
        dpg.configure_item(lock_btn_id, label="🔓")


def update_locked_nodes_positions():
    """Update positions of locked nodes to follow their highlight boxes"""
    if not hasattr(app_state, 'highlight_properties'):
        return

    for label, props in app_state.highlight_properties.items():
        if not props.get("locked", False):
            continue

        # Get the box node ID
        box_node_id = app_state.highlight_boxes.get(label)
        if not box_node_id or not dpg.does_item_exist(box_node_id):
            continue

        # Get current box position
        box_pos = dpg.get_item_pos(box_node_id)
        box_x, box_y = box_pos

        # Update each locked node
        for node_data in props.get("locked_nodes", []):
            node_id = node_data["id"]

            if dpg.does_item_exist(node_id):
                # Calculate new position based on stored offset
                new_x = box_x + node_data["offset_x"]
                new_y = box_y + node_data["offset_y"]

                dpg.set_item_pos(node_id, [new_x, new_y])