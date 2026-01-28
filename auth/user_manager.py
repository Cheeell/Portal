# ===========================================
# FILE: auth/user_manager.py
# ===========================================

import hashlib
import base64
import os
import json
import secrets
from datetime import datetime, timedelta
from config import USERS_FILE, COLORS_FILE

LAST_LOGIN_FILE = "last_login.dat"
SESSION_FILE = "session.dat"
SESSION_DURATION_DAYS = 14


def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def _get_encryption_key():
    """Generate a consistent encryption key based on machine"""
    import platform
    machine_id = platform.node() + platform.system()
    return hashlib.sha256(machine_id.encode()).digest()


def _encrypt_data(data):
    """Simple XOR encryption for data"""
    key = _get_encryption_key()
    encrypted = bytearray()

    data_bytes = data.encode('utf-8')
    for i, byte in enumerate(data_bytes):
        encrypted.append(byte ^ key[i % len(key)])

    return base64.b64encode(bytes(encrypted)).decode('utf-8')


def _decrypt_data(encrypted_data):
    """Decrypt XOR encrypted data"""
    try:
        key = _get_encryption_key()
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key[i % len(key)])

        return bytes(decrypted).decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""


def save_user_color(username, color):
    """Save user's custom color"""
    colors = load_colors()
    colors[username] = f"{int(color[0])},{int(color[1])},{int(color[2])}"

    with open(COLORS_FILE, 'w', encoding='utf-8') as f:
        for user, col in colors.items():
            f.write(f"{user}:{col}\n")


def load_colors():
    """Load all user colors"""
    colors = {}
    if os.path.exists(COLORS_FILE):
        with open(COLORS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    colors[parts[0]] = parts[1]
    return colors


def get_all_users():
    """Get list of all registered users"""
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 2:
                    users.append(parts[0])
    return users


def get_user_color(username):
    """Get user's custom color"""
    colors = load_colors()
    if username in colors:
        rgb = colors[username].split(',')
        return [int(float(rgb[0])), int(float(rgb[1])), int(float(rgb[2]))]
    return [255, 255, 255]


def register_user(username, password, color):
    """Register a new user"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                stored_user = line.strip().split(':')[0]
                if stored_user == username:
                    return False, "Username already exists!"

    with open(USERS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}:{hash_password(password)}\n")

    save_user_color(username, color)
    return True, "Registration successful!"


def login_user(username, password):
    """Verify user credentials"""
    if not os.path.exists(USERS_FILE):
        return False, "No users registered yet!"

    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 2:
                stored_user, stored_hash = parts
                if stored_user == username and stored_hash == hash_password(password):
                    return True, "Login successful!"

    return False, "Invalid username or password!"


def save_last_login(username):
    """Save the last logged in username (encrypted)"""
    try:
        encrypted_username = _encrypt_data(username)
        with open(LAST_LOGIN_FILE, 'w', encoding='utf-8') as f:
            f.write(encrypted_username)
    except Exception as e:
        print(f"Error saving last login: {e}")


def get_last_login():
    """Get the last logged in username (decrypt)"""
    if os.path.exists(LAST_LOGIN_FILE):
        try:
            with open(LAST_LOGIN_FILE, 'r', encoding='utf-8') as f:
                encrypted_data = f.read().strip()
                if encrypted_data:
                    return _decrypt_data(encrypted_data)
        except Exception as e:
            print(f"Error reading last login: {e}")
            try:
                os.remove(LAST_LOGIN_FILE)
            except:
                pass
    return ""


def create_session(username, remember_me=False):
    """Create a secure session token for auto-login"""
    if not remember_me:
        # Clear any existing session
        clear_session()
        return

    try:
        # Generate a secure random token
        token = secrets.token_urlsafe(32)

        # Create session data
        session_data = {
            "username": username,
            "token": token,
            "expires": (datetime.now() + timedelta(days=SESSION_DURATION_DAYS)).isoformat()
        }

        # Encrypt and save session
        encrypted_session = _encrypt_data(json.dumps(session_data))
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            f.write(encrypted_session)

        print(f"✓ Session created for {username} (valid for {SESSION_DURATION_DAYS} days)")

    except Exception as e:
        print(f"Error creating session: {e}")


def check_session():
    """Check if there's a valid session and return username"""
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            encrypted_data = f.read().strip()

        if not encrypted_data:
            return None

        # Decrypt session data
        decrypted = _decrypt_data(encrypted_data)
        if not decrypted:
            clear_session()
            return None

        session_data = json.loads(decrypted)

        # Check if session has expired
        expires = datetime.fromisoformat(session_data["expires"])
        if datetime.now() > expires:
            print("Session expired")
            clear_session()
            return None

        # Calculate remaining days
        remaining_days = (expires - datetime.now()).days
        print(f"✓ Valid session found for {session_data['username']} ({remaining_days} days remaining)")

        return session_data["username"]

    except Exception as e:
        print(f"Error checking session: {e}")
        clear_session()
        return None


def clear_session():
    """Clear the session file"""
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
            print("Session cleared")
    except Exception as e:
        print(f"Error clearing session: {e}")


def get_session_info():
    """Get information about current session"""
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            encrypted_data = f.read().strip()

        if not encrypted_data:
            return None

        decrypted = _decrypt_data(encrypted_data)
        if not decrypted:
            return None

        session_data = json.loads(decrypted)
        expires = datetime.fromisoformat(session_data["expires"])

        if datetime.now() > expires:
            return None

        remaining_days = (expires - datetime.now()).days

        return {
            "username": session_data["username"],
            "expires": expires.strftime("%Y-%m-%d %H:%M"),
            "remaining_days": remaining_days
        }

    except:
        return None