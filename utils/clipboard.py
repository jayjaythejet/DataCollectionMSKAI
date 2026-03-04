"""
Clipboard utility — copies text and returns a status message.
Falls back gracefully if pyperclip is unavailable.
"""
try:
    import pyperclip
    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False


def copy_to_clipboard(text: str) -> str:
    """
    Copy text to system clipboard.
    Returns a notification string to display in the UI.
    """
    if not _PYPERCLIP_AVAILABLE:
        return "⚠ pyperclip not installed — clipboard unavailable"
    try:
        pyperclip.copy(str(text))
        return f"✓ Copied to clipboard"
    except Exception as e:
        return f"⚠ Clipboard error: {e}"
