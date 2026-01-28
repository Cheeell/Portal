import dearpygui.dearpygui as dpg
import json
import os

THEMES_DIR = "themes"
CUSTOM_THEMES_FILE = os.path.join(THEMES_DIR, "custom_themes.json")

# Ensure themes directory exists
if not os.path.exists(THEMES_DIR):
    os.makedirs(THEMES_DIR)

# Standard themes with node editor support
STANDARD_THEMES = {
    "Dark (Default)": {
        "WindowBg": [15, 15, 15, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [20, 20, 20, 240],
        "Border": [110, 110, 128, 128],
        "FrameBg": [41, 74, 122, 138],
        "FrameBgHovered": [66, 150, 250, 102],
        "FrameBgActive": [66, 150, 250, 171],
        "TitleBg": [10, 10, 10, 255],
        "TitleBgActive": [41, 74, 122, 255],
        "MenuBarBg": [36, 36, 36, 255],
        "ScrollbarBg": [5, 5, 5, 135],
        "ScrollbarGrab": [79, 79, 79, 255],
        "CheckMark": [66, 150, 250, 255],
        "SliderGrab": [61, 133, 224, 255],
        "Button": [66, 150, 250, 102],
        "ButtonHovered": [66, 150, 250, 255],
        "ButtonActive": [15, 135, 250, 255],
        "Header": [66, 150, 250, 79],
        "HeaderHovered": [66, 150, 250, 204],
        "HeaderActive": [66, 150, 250, 255],
        "Tab": [46, 89, 148, 220],
        "TabHovered": [66, 150, 250, 204],
        "TabActive": [51, 105, 173, 255],
        "Text": [255, 255, 255, 255],
        "TextDisabled": [128, 128, 128, 255],
        # Node Editor colors
        "NodeGridBackground": [20, 20, 20, 255],
        "NodeGridLine": [60, 60, 60, 255],
        "NodeBackground": [35, 35, 40, 255],
        "NodeBackgroundHovered": [45, 45, 50, 255],
        "NodeBackgroundSelected": [55, 55, 60, 255],
        "NodeOutline": [100, 100, 100, 255],
        "NodeTitleBar": [41, 74, 122, 255],
        "NodeTitleBarHovered": [66, 150, 250, 255],
        "NodeTitleBarSelected": [51, 105, 173, 255],
        "NodeLink": [66, 150, 250, 255],
        "NodeLinkHovered": [100, 180, 255, 255],
        "NodeLinkSelected": [51, 105, 173, 255],
        "NodePin": [66, 150, 250, 255],
        "NodePinHovered": [100, 180, 255, 255],
    },
    "Light": {
        "WindowBg": [240, 240, 240, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [255, 255, 255, 240],
        "Border": [0, 0, 0, 77],
        "FrameBg": [255, 255, 255, 255],
        "FrameBgHovered": [66, 150, 250, 102],
        "FrameBgActive": [66, 150, 250, 171],
        "TitleBg": [245, 245, 245, 255],
        "TitleBgActive": [209, 209, 209, 255],
        "MenuBarBg": [219, 219, 219, 255],
        "ScrollbarBg": [245, 245, 245, 135],
        "ScrollbarGrab": [166, 166, 166, 255],
        "CheckMark": [66, 150, 250, 255],
        "SliderGrab": [61, 133, 224, 255],
        "Button": [66, 150, 250, 102],
        "ButtonHovered": [66, 150, 250, 255],
        "ButtonActive": [15, 135, 250, 255],
        "Header": [66, 150, 250, 79],
        "HeaderHovered": [66, 150, 250, 204],
        "HeaderActive": [66, 150, 250, 255],
        "Tab": [220, 220, 220, 220],
        "TabHovered": [66, 150, 250, 204],
        "TabActive": [255, 255, 255, 255],
        "Text": [0, 0, 0, 255],
        "TextDisabled": [153, 153, 153, 255],
        # Node Editor colors
        "NodeGridBackground": [255, 255, 255, 255],
        "NodeGridLine": [200, 200, 200, 255],
        "NodeBackground": [240, 240, 245, 255],
        "NodeBackgroundHovered": [230, 230, 240, 255],
        "NodeBackgroundSelected": [220, 220, 235, 255],
        "NodeOutline": [100, 100, 100, 255],
        "NodeTitleBar": [70, 130, 180, 255],
        "NodeTitleBarHovered": [90, 150, 200, 255],
        "NodeTitleBarSelected": [110, 170, 220, 255],
        "NodeLink": [70, 130, 180, 255],
        "NodeLinkHovered": [90, 150, 200, 255],
        "NodeLinkSelected": [110, 170, 220, 255],
        "NodePin": [50, 150, 50, 255],
        "NodePinHovered": [70, 170, 70, 255],
    },
    "Nord": {
        "WindowBg": [46, 52, 64, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [46, 52, 64, 240],
        "Border": [76, 86, 106, 128],
        "FrameBg": [59, 66, 82, 138],
        "FrameBgHovered": [136, 192, 208, 102],
        "FrameBgActive": [136, 192, 208, 171],
        "TitleBg": [46, 52, 64, 255],
        "TitleBgActive": [59, 66, 82, 255],
        "MenuBarBg": [46, 52, 64, 255],
        "ScrollbarBg": [46, 52, 64, 135],
        "ScrollbarGrab": [76, 86, 106, 255],
        "CheckMark": [136, 192, 208, 255],
        "SliderGrab": [136, 192, 208, 255],
        "Button": [136, 192, 208, 102],
        "ButtonHovered": [136, 192, 208, 255],
        "ButtonActive": [143, 188, 187, 255],
        "Header": [136, 192, 208, 79],
        "HeaderHovered": [136, 192, 208, 204],
        "HeaderActive": [136, 192, 208, 255],
        "Tab": [59, 66, 82, 220],
        "TabHovered": [136, 192, 208, 204],
        "TabActive": [76, 86, 106, 255],
        "Text": [236, 239, 244, 255],
        "TextDisabled": [76, 86, 106, 255],
        # Node Editor colors
        "NodeGridBackground": [46, 52, 64, 255],
        "NodeGridLine": [76, 86, 106, 255],
        "NodeBackground": [59, 66, 82, 255],
        "NodeBackgroundHovered": [67, 76, 94, 255],
        "NodeBackgroundSelected": [76, 86, 106, 255],
        "NodeOutline": [129, 161, 193, 255],
        "NodeTitleBar": [136, 192, 208, 255],
        "NodeTitleBarHovered": [143, 188, 187, 255],
        "NodeTitleBarSelected": [129, 161, 193, 255],
        "NodeLink": [136, 192, 208, 255],
        "NodeLinkHovered": [163, 190, 140, 255],
        "NodeLinkSelected": [143, 188, 187, 255],
        "NodePin": [163, 190, 140, 255],
        "NodePinHovered": [180, 200, 160, 255],
    },
    "Dracula": {
        "WindowBg": [40, 42, 54, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [40, 42, 54, 240],
        "Border": [68, 71, 90, 128],
        "FrameBg": [68, 71, 90, 138],
        "FrameBgHovered": [139, 233, 253, 102],
        "FrameBgActive": [139, 233, 253, 171],
        "TitleBg": [40, 42, 54, 255],
        "TitleBgActive": [68, 71, 90, 255],
        "MenuBarBg": [40, 42, 54, 255],
        "ScrollbarBg": [40, 42, 54, 135],
        "ScrollbarGrab": [68, 71, 90, 255],
        "CheckMark": [139, 233, 253, 255],
        "SliderGrab": [139, 233, 253, 255],
        "Button": [189, 147, 249, 102],
        "ButtonHovered": [189, 147, 249, 255],
        "ButtonActive": [255, 121, 198, 255],
        "Header": [189, 147, 249, 79],
        "HeaderHovered": [189, 147, 249, 204],
        "HeaderActive": [189, 147, 249, 255],
        "Tab": [68, 71, 90, 220],
        "TabHovered": [189, 147, 249, 204],
        "TabActive": [98, 114, 164, 255],
        "Text": [248, 248, 242, 255],
        "TextDisabled": [98, 114, 164, 255],
        # Node Editor colors
        "NodeGridBackground": [40, 42, 54, 255],
        "NodeGridLine": [68, 71, 90, 255],
        "NodeBackground": [68, 71, 90, 255],
        "NodeBackgroundHovered": [98, 114, 164, 255],
        "NodeBackgroundSelected": [98, 114, 164, 255],
        "NodeOutline": [189, 147, 249, 255],
        "NodeTitleBar": [189, 147, 249, 255],
        "NodeTitleBarHovered": [255, 121, 198, 255],
        "NodeTitleBarSelected": [139, 233, 253, 255],
        "NodeLink": [139, 233, 253, 255],
        "NodeLinkHovered": [80, 250, 123, 255],
        "NodeLinkSelected": [255, 121, 198, 255],
        "NodePin": [80, 250, 123, 255],
        "NodePinHovered": [139, 233, 253, 255],
    },
    "Gruvbox Dark": {
        "WindowBg": [40, 40, 40, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [40, 40, 40, 240],
        "Border": [80, 73, 69, 128],
        "FrameBg": [60, 56, 54, 138],
        "FrameBgHovered": [251, 241, 199, 102],
        "FrameBgActive": [251, 241, 199, 171],
        "TitleBg": [40, 40, 40, 255],
        "TitleBgActive": [60, 56, 54, 255],
        "MenuBarBg": [40, 40, 40, 255],
        "ScrollbarBg": [40, 40, 40, 135],
        "ScrollbarGrab": [80, 73, 69, 255],
        "CheckMark": [251, 241, 199, 255],
        "SliderGrab": [251, 241, 199, 255],
        "Button": [215, 153, 33, 102],
        "ButtonHovered": [215, 153, 33, 255],
        "ButtonActive": [250, 189, 47, 255],
        "Header": [215, 153, 33, 79],
        "HeaderHovered": [215, 153, 33, 204],
        "HeaderActive": [215, 153, 33, 255],
        "Tab": [60, 56, 54, 220],
        "TabHovered": [215, 153, 33, 204],
        "TabActive": [80, 73, 69, 255],
        "Text": [235, 219, 178, 255],
        "TextDisabled": [146, 131, 116, 255],
        # Node Editor colors
        "NodeGridBackground": [40, 40, 40, 255],
        "NodeGridLine": [80, 73, 69, 255],
        "NodeBackground": [60, 56, 54, 255],
        "NodeBackgroundHovered": [80, 73, 69, 255],
        "NodeBackgroundSelected": [102, 92, 84, 255],
        "NodeOutline": [215, 153, 33, 255],
        "NodeTitleBar": [215, 153, 33, 255],
        "NodeTitleBarHovered": [250, 189, 47, 255],
        "NodeTitleBarSelected": [254, 128, 25, 255],
        "NodeLink": [184, 187, 38, 255],
        "NodeLinkHovered": [215, 153, 33, 255],
        "NodeLinkSelected": [250, 189, 47, 255],
        "NodePin": [184, 187, 38, 255],
        "NodePinHovered": [215, 153, 33, 255],
    },
    "Monokai": {
        "WindowBg": [39, 40, 34, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [39, 40, 34, 240],
        "Border": [73, 72, 62, 128],
        "FrameBg": [73, 72, 62, 138],
        "FrameBgHovered": [102, 217, 239, 102],
        "FrameBgActive": [102, 217, 239, 171],
        "TitleBg": [39, 40, 34, 255],
        "TitleBgActive": [73, 72, 62, 255],
        "MenuBarBg": [39, 40, 34, 255],
        "ScrollbarBg": [39, 40, 34, 135],
        "ScrollbarGrab": [73, 72, 62, 255],
        "CheckMark": [102, 217, 239, 255],
        "SliderGrab": [102, 217, 239, 255],
        "Button": [249, 38, 114, 102],
        "ButtonHovered": [249, 38, 114, 255],
        "ButtonActive": [253, 151, 31, 255],
        "Header": [249, 38, 114, 79],
        "HeaderHovered": [249, 38, 114, 204],
        "HeaderActive": [249, 38, 114, 255],
        "Tab": [73, 72, 62, 220],
        "TabHovered": [249, 38, 114, 204],
        "TabActive": [102, 217, 239, 255],
        "Text": [248, 248, 242, 255],
        "TextDisabled": [117, 113, 94, 255],
        # Node Editor colors
        "NodeGridBackground": [39, 40, 34, 255],
        "NodeGridLine": [73, 72, 62, 255],
        "NodeBackground": [73, 72, 62, 255],
        "NodeBackgroundHovered": [90, 89, 77, 255],
        "NodeBackgroundSelected": [117, 113, 94, 255],
        "NodeOutline": [249, 38, 114, 255],
        "NodeTitleBar": [249, 38, 114, 255],
        "NodeTitleBarHovered": [253, 151, 31, 255],
        "NodeTitleBarSelected": [102, 217, 239, 255],
        "NodeLink": [102, 217, 239, 255],
        "NodeLinkHovered": [166, 226, 46, 255],
        "NodeLinkSelected": [249, 38, 114, 255],
        "NodePin": [166, 226, 46, 255],
        "NodePinHovered": [102, 217, 239, 255],
    },
    "Solarized Dark": {
        "WindowBg": [0, 43, 54, 240],
        "ChildBg": [0, 0, 0, 0],
        "PopupBg": [0, 43, 54, 240],
        "Border": [7, 54, 66, 128],
        "FrameBg": [7, 54, 66, 138],
        "FrameBgHovered": [42, 161, 152, 102],
        "FrameBgActive": [42, 161, 152, 171],
        "TitleBg": [0, 43, 54, 255],
        "TitleBgActive": [7, 54, 66, 255],
        "MenuBarBg": [0, 43, 54, 255],
        "ScrollbarBg": [0, 43, 54, 135],
        "ScrollbarGrab": [7, 54, 66, 255],
        "CheckMark": [42, 161, 152, 255],
        "SliderGrab": [42, 161, 152, 255],
        "Button": [38, 139, 210, 102],
        "ButtonHovered": [38, 139, 210, 255],
        "ButtonActive": [42, 161, 152, 255],
        "Header": [38, 139, 210, 79],
        "HeaderHovered": [38, 139, 210, 204],
        "HeaderActive": [38, 139, 210, 255],
        "Tab": [7, 54, 66, 220],
        "TabHovered": [38, 139, 210, 204],
        "TabActive": [88, 110, 117, 255],
        "Text": [131, 148, 150, 255],
        "TextDisabled": [88, 110, 117, 255],
        # Node Editor colors
        "NodeGridBackground": [0, 43, 54, 255],
        "NodeGridLine": [7, 54, 66, 255],
        "NodeBackground": [7, 54, 66, 255],
        "NodeBackgroundHovered": [88, 110, 117, 255],
        "NodeBackgroundSelected": [101, 123, 131, 255],
        "NodeOutline": [38, 139, 210, 255],
        "NodeTitleBar": [38, 139, 210, 255],
        "NodeTitleBarHovered": [42, 161, 152, 255],
        "NodeTitleBarSelected": [133, 153, 0, 255],
        "NodeLink": [42, 161, 152, 255],
        "NodeLinkHovered": [133, 153, 0, 255],
        "NodeLinkSelected": [38, 139, 210, 255],
        "NodePin": [133, 153, 0, 255],
        "NodePinHovered": [42, 161, 152, 255],
    },
    "ObsidianDark": {
        "Text": [220, 220, 220, 255],
        "TextDisabled": [130, 130, 130, 255],
        "WindowBg": [30, 30, 30, 255],
        "ChildBg": [25, 25, 25, 255],
        "PopupBg": [32, 32, 32, 255],
        "Border": [60, 60, 60, 160],
        "BorderShadow": [0, 0, 0, 0],
        "FrameBg": [45, 45, 45, 255],
        "FrameBgHovered": [60, 60, 60, 255],
        "FrameBgActive": [70, 70, 70, 255],
        "TitleBg": [28, 28, 28, 255],
        "TitleBgActive": [38, 38, 38, 255],
        "TitleBgCollapsed": [28, 28, 28, 200],
        "MenuBarBg": [28, 28, 28, 255],
        "ScrollbarBg": [25, 25, 25, 255],
        "ScrollbarGrab": [60, 60, 60, 255],
        "ScrollbarGrabHovered": [75, 75, 75, 255],
        "ScrollbarGrabActive": [90, 90, 90, 255],
        "CheckMark": [120, 180, 255, 255],
        "SliderGrab": [100, 100, 100, 255],
        "SliderGrabActive": [140, 140, 140, 255],
        "Button": [50, 50, 50, 255],
        "ButtonHovered": [65, 65, 65, 255],
        "ButtonActive": [80, 80, 80, 255],
        "Header": [45, 45, 45, 255],
        "HeaderHovered": [65, 65, 65, 255],
        "HeaderActive": [85, 85, 85, 255],
        "Separator": [60, 60, 60, 180],
        "SeparatorHovered": [90, 90, 90, 255],
        "SeparatorActive": [120, 120, 120, 255],
        "Tab": [38, 38, 38, 255],
        "TabHovered": [65, 65, 65, 255],
        "TabActive": [50, 50, 50, 255],
        "TabUnfocused": [32, 32, 32, 255],
        "TabUnfocusedActive": [45, 45, 45, 255],
        "DockingPreview": [120, 180, 255, 80],
        "DockingEmptyBg": [25, 25, 25, 255],
        "PlotLines": [160, 160, 160, 255],
        "PlotLinesHovered": [255, 180, 100, 255],
        "PlotHistogram": [160, 160, 160, 255],
        "PlotHistogramHovered": [255, 180, 100, 255],
        "TableHeaderBg": [40, 40, 40, 255],
        "TableBorderStrong": [70, 70, 70, 255],
        "TableBorderLight": [50, 50, 50, 255],
        "TableRowBg": [30, 30, 30, 255],
        "TableRowBgAlt": [35, 35, 35, 255],
        "TextSelectedBg": [80, 80, 80, 255],
        "DragDropTarget": [255, 200, 120, 255],
        "NavHighlight": [120, 180, 255, 255],
        "NavWindowingHighlight": [255, 255, 255, 180],
        "NavWindowingDimBg": [0, 0, 0, 120],
        "ModalWindowDimBg": [0, 0, 0, 150],
        # Node Editor colors
        "NodeGridBackground": [25, 25, 25, 255],
        "NodeGridLine": [45, 45, 45, 255],
        "NodeBackground": [45, 45, 45, 255],
        "NodeBackgroundHovered": [60, 60, 60, 255],
        "NodeBackgroundSelected": [70, 70, 70, 255],
        "NodeOutline": [100, 100, 100, 255],
        "NodeTitleBar": [38, 38, 38, 255],
        "NodeTitleBarHovered": [65, 65, 65, 255],
        "NodeTitleBarSelected": [80, 80, 80, 255],
        "NodeLink": [120, 180, 255, 255],
        "NodeLinkHovered": [150, 200, 255, 255],
        "NodeLinkSelected": [100, 160, 255, 255],
        "NodePin": [120, 180, 255, 255],
        "NodePinHovered": [150, 200, 255, 255],
    },
}

# Mapping from theme color names to DearPyGui constants
NODE_COLOR_MAPPING = {
    "NodeGridBackground": dpg.mvNodeCol_GridBackground,
    "NodeGridLine": dpg.mvNodeCol_GridLine,
    "NodeBackground": dpg.mvNodeCol_NodeBackground,
    "NodeBackgroundHovered": dpg.mvNodeCol_NodeBackgroundHovered,
    "NodeBackgroundSelected": dpg.mvNodeCol_NodeBackgroundSelected,
    "NodeOutline": dpg.mvNodeCol_NodeOutline,
    "NodeTitleBar": dpg.mvNodeCol_TitleBar,
    "NodeTitleBarHovered": dpg.mvNodeCol_TitleBarHovered,
    "NodeTitleBarSelected": dpg.mvNodeCol_TitleBarSelected,
    "NodeLink": dpg.mvNodeCol_Link,
    "NodeLinkHovered": dpg.mvNodeCol_LinkHovered,
    "NodeLinkSelected": dpg.mvNodeCol_LinkSelected,
    "NodePin": dpg.mvNodeCol_Pin,
    "NodePinHovered": dpg.mvNodeCol_PinHovered,
}


def load_custom_themes():
    """Load custom themes from file"""
    if os.path.exists(CUSTOM_THEMES_FILE):
        try:
            with open(CUSTOM_THEMES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_custom_themes(custom_themes):
    """Save custom themes to file"""
    with open(CUSTOM_THEMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(custom_themes, f, indent=2)


def get_all_themes():
    """Get all available themes (standard + custom)"""
    all_themes = dict(STANDARD_THEMES)
    custom = load_custom_themes()
    all_themes.update(custom)
    return all_themes


def apply_theme(theme_name):
    """Apply a theme to the application including node editor colors"""
    all_themes = get_all_themes()

    if theme_name not in all_themes:
        theme_name = "Dark (Default)"

    theme_data = all_themes[theme_name]

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # Apply standard UI colors
            for color_name, color_value in theme_data.items():
                # Skip node editor colors in this pass
                if color_name.startswith("Node"):
                    continue

                color_constant = getattr(dpg, f"mvThemeCol_{color_name}", None)
                if color_constant:
                    dpg.add_theme_color(color_constant, color_value)

        # Apply node editor colors
        with dpg.theme_component(dpg.mvAll, enabled_state=True):
            for color_name, color_value in theme_data.items():
                if color_name in NODE_COLOR_MAPPING:
                    dpg.add_theme_color(
                        NODE_COLOR_MAPPING[color_name],
                        color_value,
                        category=dpg.mvThemeCat_Nodes
                    )

    dpg.bind_theme(global_theme)

    # Save current theme preference
    save_theme_preference(theme_name)


def save_theme_preference(theme_name):
    """Save the current theme preference"""
    pref_file = os.path.join(THEMES_DIR, "current_theme.txt")
    with open(pref_file, 'w', encoding='utf-8') as f:
        f.write(theme_name)


def load_theme_preference():
    """Load the saved theme preference"""
    pref_file = os.path.join(THEMES_DIR, "current_theme.txt")
    if os.path.exists(pref_file):
        with open(pref_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return "Dark (Default)"


def create_custom_theme(theme_name, base_theme_name=None):
    """Create a new custom theme based on an existing theme"""
    if base_theme_name and base_theme_name in get_all_themes():
        base_theme = get_all_themes()[base_theme_name].copy()
    else:
        base_theme = STANDARD_THEMES["Dark (Default)"].copy()

    custom_themes = load_custom_themes()
    custom_themes[theme_name] = base_theme
    save_custom_themes(custom_themes)

    return base_theme


def update_custom_theme(theme_name, color_name, color_value):
    """Update a specific color in a custom theme"""
    custom_themes = load_custom_themes()

    if theme_name not in custom_themes:
        return False

    custom_themes[theme_name][color_name] = color_value
    save_custom_themes(custom_themes)
    return True


def delete_custom_theme(theme_name):
    """Delete a custom theme"""
    custom_themes = load_custom_themes()

    if theme_name in custom_themes:
        del custom_themes[theme_name]
        save_custom_themes(custom_themes)
        return True
    return False


def is_custom_theme(theme_name):
    """Check if a theme is custom (not standard)"""
    return theme_name not in STANDARD_THEMES


def get_node_colors():
    """Get all available node color names"""
    return list(NODE_COLOR_MAPPING.keys())


def get_ui_colors():
    """Get all available UI color names (excluding node colors)"""
    sample_theme = STANDARD_THEMES["Dark (Default)"]
    return [color for color in sample_theme.keys() if not color.startswith("Node")]