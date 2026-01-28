# ===========================================
# FILE: ui/dialogs.py (COMPLETE WITH FONT SELECTION)
# ===========================================

import dearpygui.dearpygui as dpg
from config import app_state
from auth.user_manager import save_user_color, get_session_info, clear_session
from scripts.script_manager import stop_script
import os

# Add font configuration storage
FONT_CONFIG_FILE = "font_settings.txt"


def get_available_fonts():
    """Get list of available fonts from fonts directory"""
    fonts_dir = "fonts"
    if not os.path.exists(fonts_dir):
        return []

    fonts = []
    for filename in os.listdir(fonts_dir):
        if filename.endswith(('.ttf', '.otf', '.ttc')):
            fonts.append(filename)

    return sorted(fonts)


def save_font_preference(font_name, font_size):
    """Save font preference to file"""
    try:
        with open(FONT_CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(f"{font_name}\n{font_size}")
        print(f"✓ Font preference saved: {font_name} @ {font_size}px")
    except Exception as e:
        print(f"Error saving font preference: {e}")


def load_font_preference():
    """Load font preference from file"""
    if os.path.exists(FONT_CONFIG_FILE):
        try:
            with open(FONT_CONFIG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                font_name = lines[0].strip() if len(lines) > 0 else "main.otf"
                font_size = int(lines[1].strip()) if len(lines) > 1 else 13
                return font_name, font_size
        except:
            pass
    return "main.otf", 13


def show_settings():
    """Show Aseprite-style settings window with sidebar"""
    dialog_id = "settings_window"

    if dpg.does_item_exist(dialog_id):
        dpg.delete_item(dialog_id)

    with dpg.window(label="Preferences", tag=dialog_id, modal=True,
                    width=900, height=700, pos=[100, 50]):
        with dpg.group(horizontal=True):
            # Left sidebar menu
            with dpg.child_window(width=180, height=650, border=True):
                dpg.add_text("Settings", color=(200, 200, 255))
                dpg.add_separator()

                # Menu buttons
                dpg.add_button(label="General", width=160, height=30,
                               callback=lambda: switch_settings_panel("general"))
                dpg.add_button(label="User Profile", width=160, height=30,
                               callback=lambda: switch_settings_panel("profile"))
                dpg.add_button(label="Appearance", width=160, height=30,
                               callback=lambda: switch_settings_panel("appearance"))
                dpg.add_button(label="Node Layout", width=160, height=30,
                               callback=lambda: switch_settings_panel("layout"))
                dpg.add_button(label="Security", width=160, height=30,
                               callback=lambda: switch_settings_panel("security"))
                dpg.add_button(label="Experimental", width=160, height=30,
                               callback=lambda: switch_settings_panel("experimental"))
                dpg.add_button(label="About", width=160, height=30,
                               callback=lambda: switch_settings_panel("about"))

                dpg.add_separator()
                dpg.add_button(label="Reset All", width=160, height=30,
                               callback=show_reset_confirmation,
                               tag="reset_button")

            # Right content area
            with dpg.child_window(width=690, height=650, border=True, tag="settings_content"):
                # Default panel
                create_general_panel()

        dpg.add_separator()

        # Bottom buttons
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=580)
            dpg.add_button(label="OK", width=80, height=30,
                           callback=lambda: save_and_close_settings())
            dpg.add_button(label="Apply", width=80, height=30,
                           callback=apply_settings)
            dpg.add_button(label="Cancel", width=80, height=30,
                           callback=lambda: dpg.delete_item(dialog_id))


def switch_settings_panel(panel_name):
    """Switch between different settings panels"""
    if dpg.does_item_exist("settings_content"):
        dpg.delete_item("settings_content", children_only=True)

        if panel_name == "general":
            create_general_panel()
        elif panel_name == "profile":
            create_profile_panel()
        elif panel_name == "appearance":
            create_appearance_panel()
        elif panel_name == "layout":
            create_layout_panel()
        elif panel_name == "security":
            create_security_panel()
        elif panel_name == "experimental":
            create_experimental_panel()
        elif panel_name == "about":
            create_about_panel()


def create_general_panel():
    """Create general settings panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("General", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # User Interface section
        dpg.add_text("User Interface:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        with dpg.group(horizontal=True):
            dpg.add_text("Window Size:", width=150)
            dpg.add_combo(["800x600", "1024x768", "1280x720", "1920x1080"],
                          default_value="800x600", width=200, tag="window_size_combo")

        with dpg.group(horizontal=True):
            dpg.add_text("UI Scale:", width=150)
            dpg.add_slider_int(default_value=100, min_value=80, max_value=200,
                               width=200, tag="ui_scale_slider", format="%d%%")

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # Behavior section
        dpg.add_text("Behavior:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Auto-save node positions every 5 seconds",
                         default_value=True, tag="autosave_checkbox")
        dpg.add_checkbox(label="Show node editor minimap",
                         default_value=True, tag="minimap_checkbox")
        dpg.add_checkbox(label="Enable keyboard shortcuts",
                         default_value=True, tag="shortcuts_checkbox")
        dpg.add_checkbox(label="Confirm before deleting nodes",
                         default_value=False, tag="confirm_delete_checkbox")

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("", tag="general_message")


def create_profile_panel():
    """Create user profile panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("User Profile", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # Current user info
        with dpg.group(horizontal=True):
            dpg.add_text("Logged in as:", width=120)
            dpg.add_text(app_state.current_user, color=app_state.current_user_color)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # User color customization
        dpg.add_text("User Color:", color=(180, 180, 180))
        dpg.add_text("This color represents you in chats and nodes",
                     color=(150, 150, 150), wrap=650)
        dpg.add_spacer(height=10)

        dpg.add_color_edit(tag="profile_color_picker",
                           default_value=app_state.current_user_color + [255],
                           no_alpha=True, width=300)

        with dpg.group(horizontal=True):
            dpg.add_text("Preview: ", width=80)
            dpg.add_text(app_state.current_user, tag="profile_color_preview",
                         color=app_state.current_user_color)

        dpg.set_item_callback("profile_color_picker",
                              lambda s, a: dpg.configure_item("profile_color_preview",
                                                              color=a[:3]))

        dpg.add_spacer(height=20)
        dpg.add_button(label="Save Color Changes", width=150,
                       callback=save_profile_color)

        dpg.add_spacer(height=10)
        dpg.add_text("", tag="profile_message")


def create_appearance_panel():
    """Create appearance/theme panel with font selection"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("Appearance", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        from themes.theme_manager import get_all_themes, load_theme_preference

        current_theme = load_theme_preference()
        all_themes = get_all_themes()
        theme_names = list(all_themes.keys())

        # === THEME SECTION ===
        dpg.add_text("Theme:", color=(180, 180, 180))
        dpg.add_text("Choose a color scheme for the interface",
                     color=(150, 150, 150), wrap=650)
        dpg.add_spacer(height=10)

        dpg.add_combo(items=theme_names, default_value=current_theme,
                      width=300, tag="theme_combo",
                      callback=preview_theme_from_panel)

        dpg.add_spacer(height=15)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply Theme", width=120,
                           callback=apply_theme_from_panel)
            dpg.add_button(label="Create Custom", width=120,
                           callback=open_theme_editor_from_panel)
            dpg.add_button(label="Advanced Settings", width=140,
                           callback=open_full_theme_settings)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # === FONT SECTION ===
        dpg.add_text("Font Settings:", color=(180, 180, 180))
        dpg.add_text("Customize the application font and size",
                     color=(150, 150, 150), wrap=650)
        dpg.add_spacer(height=10)

        # Get available fonts
        available_fonts = get_available_fonts()
        current_font, current_size = load_font_preference()

        if not available_fonts:
            dpg.add_text("⚠️ No fonts found in fonts/ directory",
                         color=(255, 200, 100))
            dpg.add_text("Place .ttf, .otf, or .ttc files in the fonts/ folder",
                         color=(150, 150, 150), wrap=650)
        else:
            # Font selection
            dpg.add_text("Font Family:")
            dpg.add_combo(items=available_fonts,
                          default_value=current_font if current_font in available_fonts else available_fonts[0],
                          width=300, tag="font_family_combo")

            dpg.add_spacer(height=10)

            # Font size slider
            dpg.add_text("Font Size:")
            dpg.add_slider_int(tag="font_size_slider", width=300,
                               default_value=current_size,
                               min_value=8, max_value=24,
                               format="%d px")

            dpg.add_spacer(height=10)

            # Font preview
            dpg.add_text("Preview:", color=(150, 200, 255))
            dpg.add_text("The quick brown fox jumps over the lazy dog 0123456789",
                         tag="font_preview_text", wrap=650)
            dpg.add_text("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя",
                         tag="font_preview_cyrillic", wrap=650)

            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True):
                dpg.add_button(label="Apply Font", width=120,
                               callback=apply_font_from_panel)
                dpg.add_button(label="Reset to Default", width=140,
                               callback=reset_font_to_default)

            dpg.add_spacer(height=10)
            dpg.add_text("⚠️ Changing fonts requires application restart",
                         color=(255, 200, 100), wrap=650)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # === PREVIEW SECTION ===
        dpg.add_text("Theme Preview:", color=(180, 180, 180))
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Button", width=100)
            dpg.add_checkbox(label="Checkbox")
            dpg.add_input_text(hint="Input field", width=150)

        with dpg.group(horizontal=True):
            dpg.add_slider_int(label="Slider", width=200, max_value=100)

        dpg.add_spacer(height=10)
        dpg.add_text("", tag="appearance_message")


def apply_font_from_panel():
    """Apply selected font settings"""
    available_fonts = get_available_fonts()

    if not available_fonts:
        dpg.set_value("appearance_message", "⚠️ No fonts available!")
        dpg.configure_item("appearance_message", color=(255, 200, 100))
        return

    font_name = dpg.get_value("font_family_combo")
    font_size = dpg.get_value("font_size_slider")

    # Save preference
    save_font_preference(font_name, font_size)

    dpg.set_value("appearance_message",
                  f"✓ Font settings saved: {font_name} @ {font_size}px\n⚠️ Please restart the application for changes to take effect")
    dpg.configure_item("appearance_message", color=(100, 255, 100))


def reset_font_to_default():
    """Reset font to default settings"""
    save_font_preference("main.otf", 13)

    if dpg.does_item_exist("font_family_combo"):
        dpg.set_value("font_family_combo", "main.otf")
    if dpg.does_item_exist("font_size_slider"):
        dpg.set_value("font_size_slider", 13)

    dpg.set_value("appearance_message",
                  "✓ Font reset to default (main.otf @ 13px)\n⚠️ Please restart the application")
    dpg.configure_item("appearance_message", color=(100, 255, 100))


def create_layout_panel():
    """Create node layout panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("Node Layout", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        dpg.add_text("Save & Load Positions:", color=(180, 180, 180))
        dpg.add_text("Manage the positions of all nodes on the board",
                     color=(150, 150, 150), wrap=650)
        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Save Layout Now", width=140, height=35,
                           callback=manual_save_positions)
            dpg.add_button(label="Load Saved Layout", width=140, height=35,
                           callback=manual_load_positions)
            dpg.add_button(label="Reset to Default", width=140, height=35,
                           callback=reset_layout_positions)

        dpg.add_spacer(height=10)
        dpg.add_text("", tag="layout_message")

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("Auto-Save:", color=(180, 180, 180))
        dpg.add_checkbox(label="Automatically save node positions every 5 seconds",
                         default_value=True, tag="layout_autosave_checkbox")

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("Debug Information:", color=(180, 180, 180))
        dpg.add_button(label="Show Current State in Console", width=220,
                       callback=debug_show_state)
        dpg.add_text("Check console for detailed node information",
                     color=(150, 150, 150))


def create_security_panel():
    """Create security panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("Security", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        # Session info
        session_info = get_session_info()

        dpg.add_text("Auto-Login Status:", color=(180, 180, 180))
        dpg.add_spacer(height=10)

        if session_info:
            dpg.add_text("✓ Auto-login is ACTIVE", color=(100, 255, 100))
            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True):
                dpg.add_text("Session expires:", width=150)
                dpg.add_text(session_info['expires'], color=(200, 200, 200))

            with dpg.group(horizontal=True):
                dpg.add_text("Days remaining:", width=150)
                dpg.add_text(f"{session_info['remaining_days']} days",
                             color=(200, 200, 200))

            dpg.add_spacer(height=15)
            dpg.add_button(label="Disable Auto-Login (Clear Session)",
                           width=250, height=35,
                           callback=clear_session_callback)
            dpg.add_text("You will need to log in again next time",
                         color=(150, 150, 150))
        else:
            dpg.add_text("✗ Auto-login is DISABLED", color=(255, 200, 100))
            dpg.add_spacer(height=5)
            dpg.add_text("Enable 'Remember me' on the login screen to activate",
                         color=(150, 150, 150), wrap=650)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("Password:", color=(180, 180, 180))
        dpg.add_button(label="Change Password", width=150,
                       callback=show_change_password_dialog)
        dpg.add_text("(Feature coming soon)", color=(150, 150, 150))

        dpg.add_spacer(height=10)
        dpg.add_text("", tag="security_message")


def create_experimental_panel():
    """Create experimental features panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("🧪 Experimental Features", color=(255, 200, 100))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        dpg.add_text("⚠️ Warning: These features are experimental and may be unstable",
                     color=(255, 150, 50), wrap=650)
        dpg.add_spacer(height=15)

        # === Background Music Section ===
        dpg.add_text("🎵 Background Music:", color=(180, 180, 255))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Enable background music player",
                         default_value=False, tag="exp_bg_music")
        dpg.add_text("Play music from music/ folder while working",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        # Music controls (initially hidden)
        with dpg.group(tag="music_controls_group", show=False):
            dpg.add_separator()
            dpg.add_text("🎵 Music Controls:", color=(150, 200, 255), indent=25)
            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True, indent=25):
                dpg.add_button(label="▶️ Play", width=80, callback=start_background_music,
                               tag="music_play_btn")
                dpg.add_button(label="⏸️ Stop", width=80, callback=stop_background_music)
                dpg.add_button(label="⏭️ Next", width=80, callback=next_music_track)
                dpg.add_button(label="🔀 Shuffle", width=80, callback=toggle_music_shuffle,
                               tag="music_shuffle_btn")
                dpg.add_button(label="🔁 Loop", width=80, callback=toggle_music_loop,
                               tag="music_loop_btn")

            dpg.add_spacer(height=5)

            with dpg.group(horizontal=True, indent=25):
                dpg.add_text("Volume:", width=60)
                dpg.add_slider_float(tag="music_volume_slider", width=300,
                                     default_value=0.5, min_value=0.0, max_value=1.0,
                                     callback=update_music_volume, format="%.2f")

            dpg.add_spacer(height=5)
            dpg.add_text("", tag="music_status_text", color=(150, 200, 255), indent=25)
            dpg.add_text("💡 Place .mp3, .wav, .ogg files in music/ folder",
                         color=(150, 150, 150), indent=25, wrap=600)
            dpg.add_separator()

        # Add callback to show/hide music controls
        dpg.set_item_callback("exp_bg_music", toggle_music_controls)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # Node Editor Features
        dpg.add_text("Node Editor:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Enable node snapping to grid",
                         default_value=False, tag="exp_node_snap")
        dpg.add_text("Snap nodes to invisible grid when moving",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Enable node linking (connections)",
                         default_value=False, tag="exp_node_links")
        dpg.add_text("Connect nodes with visual links (work in progress)",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Multi-select nodes (Ctrl+Click)",
                         default_value=False, tag="exp_multi_select")
        dpg.add_text("Select multiple nodes and move them together",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # Chat Features
        dpg.add_text("Chat & Messaging:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Enable real-time chat updates",
                         default_value=False, tag="exp_realtime_chat")
        dpg.add_text("Auto-refresh chat messages every 2 seconds",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Enable chat reactions (emoji)",
                         default_value=False, tag="exp_chat_reactions")
        dpg.add_text("React to messages with emoji (👍 ❤️ 😂)",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Enable voice messages",
                         default_value=False, tag="exp_voice_messages")
        dpg.add_text("Record and send voice messages in chats",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # Performance Features
        dpg.add_text("Performance:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Hardware acceleration (GPU)",
                         default_value=False, tag="exp_gpu_accel")
        dpg.add_text("Use GPU for rendering (requires restart)",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Lazy loading for large chats",
                         default_value=False, tag="exp_lazy_load")
        dpg.add_text("Load chat messages on demand for better performance",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        # Advanced Features
        dpg.add_text("Advanced:", color=(180, 180, 180))
        dpg.add_spacer(height=5)

        dpg.add_checkbox(label="Enable plugin system",
                         default_value=False, tag="exp_plugins")
        dpg.add_text("Load custom Python plugins from plugins/ folder",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Enable AI assistant integration",
                         default_value=False, tag="exp_ai_assistant")
        dpg.add_text("Chat with AI assistant for help and suggestions",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=10)

        dpg.add_checkbox(label="Enable cloud sync (beta)",
                         default_value=False, tag="exp_cloud_sync")
        dpg.add_text("Sync your data across devices (requires account)",
                     color=(150, 150, 150), wrap=620, indent=25)

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("", tag="experimental_message")

        dpg.add_spacer(height=10)

        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply Experimental Settings", width=200,
                           callback=apply_experimental_settings)
            dpg.add_button(label="Reset All to Defaults", width=180,
                           callback=reset_experimental_settings)


# === Background Music Callbacks ===

def toggle_music_controls(sender, app_data):
    """Show/hide music controls based on checkbox"""
    if dpg.does_item_exist("music_controls_group"):
        dpg.configure_item("music_controls_group", show=app_data)


def start_background_music():
    """Start playing background music"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        success = manager.play()

        if success:
            update_music_status()
        else:
            if dpg.does_item_exist("music_status_text"):
                dpg.set_value("music_status_text", "❌ No music files found in music/ folder")
    except Exception as e:
        print(f"Error starting music: {e}")
        if dpg.does_item_exist("music_status_text"):
            dpg.set_value("music_status_text", f"❌ Error: {e}")


def stop_background_music():
    """Stop background music"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        manager.stop()
        update_music_status()
    except Exception as e:
        print(f"Error stopping music: {e}")


def next_music_track():
    """Skip to next track"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        manager.next_track()
        update_music_status()
    except Exception as e:
        print(f"Error skipping track: {e}")


def toggle_music_shuffle():
    """Toggle shuffle mode"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        shuffle_on = manager.toggle_shuffle()

        if dpg.does_item_exist("music_shuffle_btn"):
            label = "🔀 Shuffle ON" if shuffle_on else "🔀 Shuffle"
            dpg.configure_item("music_shuffle_btn", label=label)

        update_music_status()
    except Exception as e:
        print(f"Error toggling shuffle: {e}")


def toggle_music_loop():
    """Toggle loop mode"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        loop_on = manager.toggle_loop()

        if dpg.does_item_exist("music_loop_btn"):
            label = "🔁 Loop ON" if loop_on else "🔁 Loop"
            dpg.configure_item("music_loop_btn", label=label)

        update_music_status()
    except Exception as e:
        print(f"Error toggling loop: {e}")


def update_music_volume(sender, app_data):
    """Update music volume"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        manager.set_volume(app_data)
    except Exception as e:
        print(f"Error updating volume: {e}")


def update_music_status():
    """Update music status display"""
    try:
        from music.background_music import get_music_manager

        manager = get_music_manager()
        status = manager.get_status()

        if dpg.does_item_exist("music_status_text"):
            if status["is_playing"]:
                text = f"▶️ Playing: {status['current_track']} ({status['current_index'] + 1}/{status['track_count']})"
                color = (100, 255, 100)
            else:
                text = f"⏸️ Stopped ({status['track_count']} tracks available)"
                color = (150, 150, 150)

            dpg.set_value("music_status_text", text)
            dpg.configure_item("music_status_text", color=color)
    except Exception as e:
        print(f"Error updating status: {e}")


def create_about_panel():
    """Create about panel"""
    with dpg.group(parent="settings_content"):
        dpg.add_text("About Messenger", color=(220, 220, 220))
        dpg.add_separator()
        dpg.add_spacer(height=10)

        dpg.add_text("Messenger Application", color=(100, 200, 255))
        dpg.add_text("Version 2.0", color=(150, 150, 150))
        dpg.add_spacer(height=15)

        dpg.add_text("A node-based messaging and collaboration system",
                     wrap=650)
        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("Features:", color=(180, 180, 180))

        features = [
            "• Multi-user chat system with mentions",
            "• Group chats with member management",
            "• Read-only chat mode",
            "• Python script execution",
            "• Text notes and labels",
            "• Image nodes with viewer",
            "• Audio playback nodes",
            "• Highlight boxes for organization",
            "• User authentication with sessions",
            "• 8 standard themes + custom themes",
            "• Custom font support",
            "• Auto-save node positions",
            "• Aseprite-style interface"
        ]

        for feature in features:
            dpg.add_text(feature, color=(200, 200, 200))

        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_spacer(height=15)

        dpg.add_text("Technology:", color=(180, 180, 180))
        dpg.add_text(f"DearPyGUI Version: {dpg.get_dearpygui_version()}",
                     color=(200, 200, 200))
        dpg.add_text("Python 3.x", color=(200, 200, 200))


# Callback functions
def save_and_close_settings():
    """Save all settings and close window"""
    apply_settings()
    if dpg.does_item_exist("settings_window"):
        dpg.delete_item("settings_window")


def apply_settings():
    """Apply current settings without closing"""
    print("Settings applied")
    # Add logic to save settings to config file


def save_profile_color():
    """Save user color changes"""
    new_color = dpg.get_value("profile_color_picker")[:3]
    app_state.current_user_color = [int(new_color[0]), int(new_color[1]), int(new_color[2])]

    save_user_color(app_state.current_user, app_state.current_user_color)

    dpg.set_value("profile_message", "✓ Color saved successfully!")
    dpg.configure_item("profile_message", color=(0, 255, 0))

    if dpg.does_item_exist("main_user_display"):
        dpg.configure_item("main_user_display", color=app_state.current_user_color)


def preview_theme_from_panel():
    """Preview selected theme"""
    from themes.theme_manager import apply_theme
    theme_name = dpg.get_value("theme_combo")
    apply_theme(theme_name)


def apply_theme_from_panel():
    """Apply and save selected theme"""
    from themes.theme_manager import apply_theme
    theme_name = dpg.get_value("theme_combo")
    apply_theme(theme_name)

    dpg.set_value("appearance_message", f"✓ Theme '{theme_name}' applied!")
    dpg.configure_item("appearance_message", color=(0, 255, 0))


def open_theme_editor_from_panel():
    """Open theme editor"""
    dpg.set_value("appearance_message", "Opening theme editor...")
    dpg.configure_item("appearance_message", color=(255, 255, 0))


def open_full_theme_settings():
    """Open full theme settings window"""
    try:
        from themes.theme_ui import show_theme_settings
        show_theme_settings()
    except Exception as e:
        print(f"Error opening theme settings: {e}")


def manual_save_positions():
    """Manually save all node positions"""
    print("\n=== MANUAL SAVE TRIGGERED ===")
    from ui.node_position_manager import save_all_node_positions

    if save_all_node_positions():
        dpg.set_value("layout_message", "✓ Layout saved successfully!")
        dpg.configure_item("layout_message", color=(0, 255, 0))
    else:
        dpg.set_value("layout_message", "✗ Save failed!")
        dpg.configure_item("layout_message", color=(255, 0, 0))


def manual_load_positions():
    """Manually load all node positions"""
    print("\n=== MANUAL LOAD TRIGGERED ===")
    from ui.node_position_manager import load_all_node_positions

    if load_all_node_positions():
        dpg.set_value("layout_message", "✓ Layout loaded successfully!")
        dpg.configure_item("layout_message", color=(0, 255, 0))
    else:
        dpg.set_value("layout_message", "✗ Load failed!")
        dpg.configure_item("layout_message", color=(255, 0, 0))


def reset_layout_positions():
    """Reset all node positions to default"""
    dpg.set_value("layout_message", "⚠ Reset feature coming soon")
    dpg.configure_item("layout_message", color=(255, 200, 0))


def debug_show_state():
    """Show debug info in console"""
    from ui.node_position_manager import debug_print_app_state
    debug_print_app_state()
    dpg.set_value("layout_message", "✓ Check console for debug info")
    dpg.configure_item("layout_message", color=(0, 255, 255))


def clear_session_callback():
    """Clear the current session"""
    clear_session()
    dpg.set_value("security_message", "✓ Session cleared - auto-login disabled")
    dpg.configure_item("security_message", color=(255, 200, 0))

    # Refresh panel to show updated status
    switch_settings_panel("security")


def show_change_password_dialog():
    """Show password change dialog"""
    dpg.set_value("security_message", "⚠ Password change feature coming soon")
    dpg.configure_item("security_message", color=(255, 200, 0))


def apply_experimental_settings():
    """Apply experimental settings"""
    dpg.set_value("experimental_message", "✓ Experimental settings applied!")
    dpg.configure_item("experimental_message", color=(0, 255, 0))
    print("\n=== EXPERIMENTAL SETTINGS ===")
    print(f"Background music: {dpg.get_value('exp_bg_music')}")
    print(f"Node snapping: {dpg.get_value('exp_node_snap')}")
    print(f"Node linking: {dpg.get_value('exp_node_links')}")
    print(f"Multi-select: {dpg.get_value('exp_multi_select')}")
    print(f"Real-time chat: {dpg.get_value('exp_realtime_chat')}")
    print(f"Chat reactions: {dpg.get_value('exp_chat_reactions')}")
    print(f"Voice messages: {dpg.get_value('exp_voice_messages')}")
    print(f"GPU acceleration: {dpg.get_value('exp_gpu_accel')}")
    print(f"Lazy loading: {dpg.get_value('exp_lazy_load')}")
    print(f"Plugins: {dpg.get_value('exp_plugins')}")
    print(f"AI assistant: {dpg.get_value('exp_ai_assistant')}")
    print(f"Cloud sync: {dpg.get_value('exp_cloud_sync')}")


def reset_experimental_settings():
    """Reset all experimental settings to defaults"""
    exp_checkboxes = [
        "exp_bg_music", "exp_node_snap", "exp_node_links", "exp_multi_select",
        "exp_realtime_chat", "exp_chat_reactions", "exp_voice_messages",
        "exp_gpu_accel", "exp_lazy_load", "exp_plugins",
        "exp_ai_assistant", "exp_cloud_sync"
    ]

    for checkbox in exp_checkboxes:
        if dpg.does_item_exist(checkbox):
            dpg.set_value(checkbox, False)

    dpg.set_value("experimental_message", "✓ All experimental features disabled")
    dpg.configure_item("experimental_message", color=(255, 200, 0))


def show_reset_confirmation():
    """Show confirmation dialog for resetting all settings"""
    confirm_id = "reset_confirm_dialog"

    if dpg.does_item_exist(confirm_id):
        dpg.delete_item(confirm_id)

    with dpg.window(label="Reset Settings", tag=confirm_id, modal=True,
                    width=400, height=150, pos=[300, 250]):
        dpg.add_text("Are you sure you want to reset all settings?", wrap=380)
        dpg.add_text("This action cannot be undone.", color=(255, 150, 0), wrap=380)
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_button(label="Reset", width=120,
                           callback=lambda: [reset_all_settings(),
                                             dpg.delete_item(confirm_id)])
            dpg.add_button(label="Cancel", width=120,
                           callback=lambda: dpg.delete_item(confirm_id))


def reset_all_settings():
    """Reset all settings to defaults"""
    print("Resetting all settings to defaults...")


def show_about():
    """Show simple about dialog"""
    create_about_panel()


def logout():
    """Logout current user"""
    for script_name in list(app_state.running_processes.keys()):
        stop_script(script_name)

    clear_session()
    print("✓ Logged out - session cleared")

    app_state.current_user = None
    app_state.current_user_color = [255, 255, 255]

    if dpg.does_item_exist("messenger_window"):
        dpg.delete_item("messenger_window")
    if dpg.does_item_exist("control_strip"):
        dpg.delete_item("control_strip")

    from auth.ui import show_login_screen
    from ui.messenger import show_messenger
    from ui.control_strip import create_control_strip

    def on_login():
        show_messenger()
        create_control_strip()

    show_login_screen(on_login)