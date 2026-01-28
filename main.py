import dearpygui.dearpygui as dpg
from auth.ui import show_login_screen
from ui.messenger import show_messenger
from ui.control_strip import create_control_strip, update_control_strip_position
from themes.theme_manager import apply_theme, load_theme_preference
import os


def load_font_settings():
    """Load font settings from config file"""
    font_config_file = "font_settings.txt"

    if os.path.exists(font_config_file):
        try:
            with open(font_config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                font_name = lines[0].strip() if len(lines) > 0 else "main.otf"
                font_size = int(lines[1].strip()) if len(lines) > 1 else 13
                return font_name, font_size
        except Exception as e:
            print(f"Error loading font settings: {e}")

    return "main.otf", 13


def change_font():
    """Load and apply custom font with user preferences"""
    font_name, font_size = load_font_settings()
    font_path = os.path.join("fonts", font_name)

    # Check if font file exists
    if not os.path.exists(font_path):
        print(f"⚠️ Font file not found: {font_path}")
        print("Using default font settings")
        font_path = "fonts/main.otf"
        font_size = 13

    with dpg.font_registry():
        try:
            with dpg.font(font_path, font_size) as default_font:
                # Add the default and extended font ranges
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Thai)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)

                dpg.bind_font(default_font)
                print(f"✓ Font loaded: {font_name} @ {font_size}px")
        except Exception as e:
            print(f"❌ Error loading font: {e}")
            print("Falling back to default system font")


def main():
    print("Starting application...")
    try:
        dpg.create_context()
        print("✓ Context created")

        dpg.create_viewport(title="Interface", width=800, height=800)
        print("✓ Viewport created")

        # Load custom font
        change_font()

        saved_theme = load_theme_preference()
        print(f"✓ Theme loaded: {saved_theme}")
        apply_theme(saved_theme)

        dpg.setup_dearpygui()
        print("✓ DearPyGUI setup complete")

        show_login_screen(on_login_success)
        print("✓ Login screen called")

        dpg.show_viewport()
        print("✓ Viewport shown")

        # Auto-save counter
        frame_count = 0
        AUTOSAVE_INTERVAL = 300

        while dpg.is_dearpygui_running():
            update_control_strip_position()

            # Update locked nodes positions (NEW)
            try:
                from nodes.highlight import update_locked_nodes_positions
                update_locked_nodes_positions()
            except Exception as e:
                pass  # Silently handle errors

            # Auto-save positions periodically
            frame_count += 1
            if frame_count >= AUTOSAVE_INTERVAL:
                try:
                    from ui.node_position_manager import save_all_node_positions
                    save_all_node_positions()
                except Exception as e:
                    print(f"Auto-save error: {e}")
                frame_count = 0

            dpg.render_dearpygui_frame()

        # Save positions before exit
        try:
            from ui.node_position_manager import save_all_node_positions
            save_all_node_positions()
            print("✓ Final save complete")
        except Exception as e:
            print(f"Exit save error: {e}")

        dpg.destroy_context()

    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


def on_login_success():
    """Called after successful login"""
    from config import app_state
    print(f"\n=== on_login_success called ===")
    print(f"Current user: {app_state.current_user}")
    print(f"User color: {app_state.current_user_color}")

    try:
        print("Creating messenger window...")
        show_messenger()
        print("✓ Messenger window created")

        print("Creating control strip...")
        create_control_strip()
        print("✓ Control strip created")

        # Setup drag and drop handlers after messenger is created
        print("Setting up drag-and-drop handlers...")
        from ui.drag_drop_handler import setup_drag_drop_handlers
        setup_drag_drop_handlers()
        print("✓ Drag-and-drop handlers ready")

        # Verify windows were created
        if dpg.does_item_exist("messenger_window"):
            print("✓ messenger_window verified")
            is_shown = dpg.is_item_shown("messenger_window")
            print(f"  Window shown: {is_shown}")
        else:
            print("✗ messenger_window NOT FOUND after creation!")

        if dpg.does_item_exist("control_strip"):
            print("✓ control_strip verified")
        else:
            print("✗ control_strip NOT FOUND after creation!")

    except Exception as e:
        print(f"ERROR in on_login_success: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()