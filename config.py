# ===========================================
# FILE: config.py
# ===========================================

import os

# Directories
CHATS_DIR = "chats"
SCRIPTS_DIR = "user_scripts"
USERS_FILE = "users.txt"
COLORS_FILE = "user_colors.txt"
FONTS_DIR = "fonts"

# Create directories
for directory in [CHATS_DIR, SCRIPTS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Global state (should be in a state manager eventually)
class AppState:
    def __init__(self):
        self.current_user = None
        self.current_user_color = [255, 255, 255]
        self.node_chats = {}
        self.chat_settings = {}
        self.script_nodes = {}
        self.highlight_boxes = {}
        self.text_nodes = {}
        self.image_nodes = {}
        self.node_editor = None
        self.audio_nodes = {}
        self.running_processes = {}
        self.click_position = [0, 0]
        self.selected_nodes = []
        self.highlight_properties = {}

app_state = AppState()