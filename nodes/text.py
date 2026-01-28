# ===========================================
# FILE: nodes/text.py (FIXED - No Black Box)
# ===========================================
import dearpygui.dearpygui as dpg
import random
import os
from config import app_state

# Directory for storing markdown notes
NOTES_DIR = "notes"
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)


def show_create_text_dialog():
    """Show dialog to create text note"""
    dialog_id = "create_text_dialog"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="Create Text Note", tag=dialog_id, modal=True,
                    width=450, height=400, pos=[225, 125]):
        dpg.add_text("Add a markdown note to the board:")
        dpg.add_separator()

        dpg.add_text("Note Title:")
        dpg.add_input_text(tag="text_title_input", width=420,
                           default_value="My Note")

        dpg.add_separator()
        dpg.add_text("Content (Markdown supported):")
        dpg.add_input_text(tag="text_content_input", width=420, height=200,
                           multiline=True,
                           default_value="# My Note\n\nEnter your content here...\n\n- Bullet point\n- Another point")

        dpg.add_text("💡 Tip: Supports markdown formatting",
                     color=(150, 150, 150))

        dpg.add_separator()
        dpg.add_text("", tag="text_create_message")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Create", width=150, callback=create_text_from_dialog)
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(dialog_id))


def create_text_from_dialog():
    """Create text node from dialog inputs"""
    title = dpg.get_value("text_title_input")
    content = dpg.get_value("text_content_input")

    if not title or not title.strip():
        dpg.set_value("text_create_message", "Please enter a title!")
        dpg.configure_item("text_create_message", color=(255, 0, 0))
        return

    if not content or not content.strip():
        dpg.set_value("text_create_message", "Please enter some content!")
        dpg.configure_item("text_create_message", color=(255, 0, 0))
        return

    create_text_node(title.strip(), content.strip())
    dpg.delete_item("create_text_dialog")


def create_text_node(title, content):
    """Create a text node on the board"""
    pos = [random.randint(50, 400), random.randint(50, 300)]
    new_node_id = dpg.generate_uuid()

    # Save content to markdown file
    filename = f"{title.replace(' ', '_')}_{new_node_id}.md"
    filepath = os.path.join(NOTES_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    text_key = f"text_{new_node_id}"
    app_state.text_nodes[text_key] = {
        "id": new_node_id,
        "title": title,
        "filepath": filepath,
        "author": app_state.current_user
    }

    # Create preview (first 100 chars)
    preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content.replace('\n', ' ')

    with dpg.node(label=f"📝 {title}", pos=pos,
                  parent=app_state.node_editor, tag=new_node_id):
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            with dpg.group(horizontal=True):
                dpg.add_text("📝 Note", color=(255, 255, 100))
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

    # Add tooltip
    with dpg.tooltip(f"view_btn_{new_node_id}"):
        dpg.add_text("Click to view full note")


def show_full_note(text_key):
    """Show full note with markdown rendering - FIXED VERSION"""
    if text_key not in app_state.text_nodes:
        return

    text_data = app_state.text_nodes[text_key]
    viewer_id = f"note_viewer_{text_key}"

    if dpg.does_item_exist(viewer_id):
        dpg.delete_item(viewer_id)

    # Read content from file
    try:
        with open(text_data["filepath"], 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        content = "Error loading note content"

    with dpg.window(label=f"📝 {text_data['title']}", tag=viewer_id,
                    width=700, height=600, pos=[150, 100], modal=False):

        with dpg.group(horizontal=True):
            dpg.add_text(f"📝 {text_data['title']}", color=(200, 200, 255))
            dpg.add_button(label="Edit", width=80,
                           callback=lambda: [dpg.delete_item(viewer_id),
                                             edit_text_node(text_key)])
            dpg.add_button(label="Close", width=80,
                           callback=lambda: dpg.delete_item(viewer_id))

        dpg.add_separator()
        dpg.add_text(f"By: {text_data['author']}",
                     color=app_state.current_user_color)
        dpg.add_separator()

        # FIXED: Display markdown content directly without child_window causing black box
        render_markdown(content, viewer_id)


def render_markdown(content, parent):
    """Simple markdown renderer for DearPyGUI - FIXED VERSION"""
    lines = content.split('\n')

    for line in lines:
        if not line.strip():
            dpg.add_spacer(height=5, parent=parent)
            continue

        # Headers
        if line.startswith('# '):
            dpg.add_text(line[2:], color=(255, 255, 150), parent=parent)
            dpg.add_separator(parent=parent)
        elif line.startswith('## '):
            dpg.add_text(line[3:], color=(200, 200, 255), parent=parent)
        elif line.startswith('### '):
            dpg.add_text(line[4:], color=(180, 180, 220), parent=parent)

        # Bullet points
        elif line.strip().startswith('- '):
            dpg.add_text("  • " + line.strip()[2:], color=(200, 200, 200),
                         wrap=650, parent=parent)
        elif line.strip().startswith('* '):
            dpg.add_text("  • " + line.strip()[2:], color=(200, 200, 200),
                         wrap=650, parent=parent)

        # Numbered lists
        elif line.strip() and line.strip()[0].isdigit() and '. ' in line:
            dpg.add_text("  " + line.strip(), color=(200, 200, 200),
                         wrap=650, parent=parent)

        # Code blocks
        elif line.strip().startswith('```'):
            dpg.add_text(line, color=(100, 255, 100), parent=parent)

        # Bold text (simple detection)
        elif '**' in line:
            dpg.add_text(line.replace('**', ''), color=(255, 255, 255),
                         wrap=650, parent=parent)

        # Regular text
        else:
            dpg.add_text(line, color=(200, 200, 200), wrap=650, parent=parent)


def edit_text_node(text_key):
    """Edit an existing text node"""
    if text_key not in app_state.text_nodes:
        return

    text_data = app_state.text_nodes[text_key]
    dialog_id = f"edit_text_dialog_{text_key}"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    # Read current content
    try:
        with open(text_data["filepath"], 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        content = ""

    with dpg.window(label="Edit Text Note", tag=dialog_id, modal=True,
                    width=500, height=450, pos=[200, 100]):
        dpg.add_text("Edit your note:")
        dpg.add_separator()

        dpg.add_text("Note Title:")
        dpg.add_input_text(tag=f"edit_text_title_{text_key}", width=470,
                           default_value=text_data["title"])

        dpg.add_separator()
        dpg.add_text("Content (Markdown supported):")
        dpg.add_input_text(tag=f"edit_text_content_{text_key}", width=470, height=250,
                           multiline=True, default_value=content)

        dpg.add_separator()
        dpg.add_text("", tag=f"edit_text_message_{text_key}")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Changes", width=150,
                           callback=lambda: save_text_edit(text_key, dialog_id))
            dpg.add_button(label="Cancel", width=150,
                           callback=lambda: dpg.delete_item(dialog_id))


def save_text_edit(text_key, dialog_id):
    """Save changes to text node"""
    if text_key not in app_state.text_nodes:
        return

    new_title = dpg.get_value(f"edit_text_title_{text_key}")
    new_content = dpg.get_value(f"edit_text_content_{text_key}")

    if not new_title or not new_title.strip():
        dpg.set_value(f"edit_text_message_{text_key}", "Please enter a title!")
        dpg.configure_item(f"edit_text_message_{text_key}", color=(255, 0, 0))
        return

    if not new_content or not new_content.strip():
        dpg.set_value(f"edit_text_message_{text_key}", "Please enter some content!")
        dpg.configure_item(f"edit_text_message_{text_key}", color=(255, 0, 0))
        return

    text_data = app_state.text_nodes[text_key]
    node_id = text_data["id"]

    # Update title
    text_data["title"] = new_title.strip()

    # Save new content to file
    try:
        with open(text_data["filepath"], 'w', encoding='utf-8') as f:
            f.write(new_content.strip())
    except Exception as e:
        dpg.set_value(f"edit_text_message_{text_key}", f"Error saving: {e}")
        dpg.configure_item(f"edit_text_message_{text_key}", color=(255, 0, 0))
        return

    # Update node label
    if dpg.does_item_exist(node_id):
        dpg.configure_item(node_id, label=f"📝 {new_title.strip()}")

    # Update preview
    preview = new_content[:100].replace('\n', ' ') + "..." if len(new_content) > 100 else new_content.replace('\n', ' ')
    if dpg.does_item_exist(f"text_preview_{node_id}"):
        dpg.set_value(f"text_preview_{node_id}", preview)

    dpg.delete_item(dialog_id)


def delete_text_node(node_id, text_key):
    """Delete a text node"""
    if dpg.does_item_exist(node_id):
        dpg.delete_item(node_id)

    if text_key in app_state.text_nodes:
        # Delete the markdown file
        filepath = app_state.text_nodes[text_key]["filepath"]
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass

        del app_state.text_nodes[text_key]