# ===========================================
# FILE: chat/message_parser.py (NEW FILE)
# ===========================================

import re
from auth.user_manager import get_user_color, get_all_users


def parse_message_with_mentions(message_text):
    """
    Parse message text and identify @mentions
    Returns list of segments with formatting info
    """
    segments = []
    all_users = get_all_users()

    # Pattern to match @username
    pattern = r'@(\w+)'

    last_end = 0
    for match in re.finditer(pattern, message_text):
        username = match.group(1)
        start, end = match.span()

        # Add text before mention
        if start > last_end:
            segments.append({
                'type': 'text',
                'content': message_text[last_end:start]
            })

        # Add mention
        if username in all_users:
            segments.append({
                'type': 'mention',
                'content': f'@{username}',
                'username': username,
                'color': get_user_color(username)
            })
        else:
            # Username not found, treat as regular text
            segments.append({
                'type': 'text',
                'content': match.group(0)
            })

        last_end = end

    # Add remaining text
    if last_end < len(message_text):
        segments.append({
            'type': 'text',
            'content': message_text[last_end:]
        })

    return segments


def format_message_for_display(raw_message):
    """
    Format a raw chat message for display with colored mentions
    Input: "[2024-01-15 10:30:00] Alice: Hey @Bob, check out @Charlie's work!"
    Output: Formatted segments list
    """
    # Extract timestamp, username, and message
    pattern = r'\[(.*?)\] (.*?): (.*)'
    match = re.match(pattern, raw_message)

    if not match:
        return [{'type': 'text', 'content': raw_message}]

    timestamp, username, message = match.groups()
    user_color = get_user_color(username)

    # Parse message content for mentions
    message_segments = parse_message_with_mentions(message)

    # Build complete formatted message
    result = [
        {'type': 'text', 'content': f'[{timestamp}] '},
        {'type': 'user', 'content': username, 'color': user_color},
        {'type': 'text', 'content': ': '}
    ]

    result.extend(message_segments)

    return result