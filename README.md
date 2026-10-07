# Portal

A desktop messenger built on a **node-based canvas**. Instead of a fixed chat list, conversations, notes, images, audio, files and scripts all live as draggable nodes on one freeform workspace. Built with Python and [Dear PyGui](https://github.com/hoffstadt/DearPyGui).

## Features

- **Node canvas workspace** – chats, text notes, images, audio clips, files, scripts and highlight boxes are all nodes you can place, move and group.
- **Chats** – one-to-one and group chats, with optional read-only mode, per-user colours and saved messages.
- **Text nodes** – notes backed by Markdown files in `notes/`.
- **Media and file nodes** – image and audio nodes with stored dimensions and paths; file nodes track name, size and extension.
- **Drag and drop** – drop files onto the canvas to create nodes.
- **Highlight boxes** – resizable, colour-tinted regions to group nodes; nodes can be locked to them.
- **Scripts** – user scripts represented as nodes and managed through a script manager.
- **Accounts** – login screen with a user manager and persistent session.
- **Themes and fonts** – built-in and custom themes, plus a configurable font (with Cyrillic, CJK, Thai, Vietnamese and Korean glyph support).
- **Background music** – plays tracks from the `music/` folder (shuffle, loop, volume) via `pygame`.
- **Persistence** – node positions and properties autosave periodically and on exit, and missing nodes are recreated on load.

## Requirements

- Python 3.13+ (the repo contains 3.13 and 3.14 bytecode)
- Dependencies from `requirements.txt`:
  - `dearpygui>=1.9.0`
  - `Pillow>=9.0.0`
  - `numpy>=1.21.0`
  - `pygame>=2.5.0`

## Installation

```bash
git clone https://github.com/Cheeell/Portal.git
cd Portal
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Log in (or create a user) on the login screen.
2. The messenger window and a floating control strip open on the canvas.
3. Create chats and nodes from the control strip, or drag files onto the canvas.
4. Positions autosave every few seconds and again when you close the app.

### Optional setup

- **Font** – edit `font_settings.txt`: line 1 is the font file name inside `fonts/` (default `main.otf`), line 2 is the size (default `13`).
- **Music** – place `.mp3`, `.wav`, `.ogg`, `.flac` or `.m4a` files in `music/`.
- **Theme** – chosen in the theme UI; stored in `themes/current_theme.txt`.

## Project structure

```
Portal/
├── main.py                 # Entry point: viewport, font, theme, main loop, autosave
├── config.py               # Paths and global AppState
├── Cassa.py                # Utility: dumps tree + .py sources into structure.txt
├── auth/                   # Login UI and user manager
├── chat/                   # Chat manager, chat nodes, message parser, saved messages
├── nodes/                  # Node types: base, text, image, audio, file, highlight
├── scripts/                # Script manager, script nodes, UI
├── themes/                 # Theme manager, theme UI, custom themes
├── ui/                     # Messenger window, control strip, dialogs,
│                           # drag-and-drop, node position manager, helpers
├── music/                  # Background music manager
├── notes/                  # Markdown notes used by text nodes
├── saved_messages/         # Per-user saved messages
├── fonts/  images/  audio/ # Assets
├── users.txt  user_colors.txt  contacts.json  call_history.json
└── node_positions.json     # Saved canvas layout
```

## Data files

| File | Purpose |
| --- | --- |
| `users.txt`, `user_colors.txt` | Accounts and their display colours |
| `contacts.json`, `call_history.json` | Contacts and call history |
| `node_positions.json` | Positions and properties of all canvas nodes |
| `font_settings.txt` | Font name and size |
| `chats/`, `user_scripts/` | Chat logs and user scripts (created on first run) |

> **Privacy note:** several of these files hold user data. Add them to `.gitignore` if you plan to keep personal data out of the repository.

## Development

`Cassa.py` generates `structure.txt` (a directory tree plus the contents of every `.py` file), which is handy for sharing the codebase. Configure exclusions in `.pyignore`; a `[tree-only]` section lists folders that appear in the tree but are not expanded.

```bash
python Cassa.py
```

`test.py` is a small standalone Dear PyGui node editor demo with a custom light theme.

## Roadmap ideas

- Move global `app_state` into a proper state manager (noted in `config.py`).
- Add a `.gitignore` for `__pycache__/`, `.DS_Store`, session and user data.
- Remove bundled binaries from `files/` (e.g. the TwitchDownloaderCLI archive).

## License

No license specified yet. Add a `LICENSE` file to clarify usage terms.
