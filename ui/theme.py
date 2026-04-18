"""UI theme palettes (light / dark) + persistence of user preference."""
import json
import os

LIGHT = {
    "BG_TOP": "#dde3ea", "BG_PROG": "#cdd3da", "BG_BOTTOM": "#dde3ea",
    "TEXT_MAIN": "#111111", "TEXT_GRAY": "#555555",
    "TEXT_GREEN": "#2e7d32", "TEXT_AMBER": "#b45000",
    "BTN_BLUE": "#1f6aa5", "BTN_GRAY": "#888888",
    "BTN_GREEN": "#2e7d32", "BTN_ORANGE": "#c07000",
    "TAB_BTN_SELECTED": "#1f6aa5", "TAB_BTN_UNSELECTED": "#e0e5ea",
    "TAB_TEXT_SELECTED": "#ffffff", "TAB_TEXT_UNSELECTED": "#111111",
    "TAB_TEXT_LABEL": "#111111", "TAB_TEXT_HEADER": "#111111",
    "TAB_TEXT_HINT": "#666666",
    "TAB_BTN_HOVER": "#c0ccd8", "TAB_BTN_BORDER": "#aab0b8",
}

DARK = {
    "BG_TOP": "#2a2d33", "BG_PROG": "#23262b", "BG_BOTTOM": "#2a2d33",
    "TEXT_MAIN": "#e5e7eb", "TEXT_GRAY": "#9ca3af",
    "TEXT_GREEN": "#4ade80", "TEXT_AMBER": "#fbbf24",
    "BTN_BLUE": "#2563eb", "BTN_GRAY": "#4b5563",
    "BTN_GREEN": "#16a34a", "BTN_ORANGE": "#d97706",
    "TAB_BTN_SELECTED": "#2563eb", "TAB_BTN_UNSELECTED": "#3a3f46",
    "TAB_TEXT_SELECTED": "#ffffff", "TAB_TEXT_UNSELECTED": "#e5e7eb",
    "TAB_TEXT_LABEL": "#e5e7eb", "TAB_TEXT_HEADER": "#e5e7eb",
    "TAB_TEXT_HINT": "#9ca3af",
    "TAB_BTN_HOVER": "#4b5563", "TAB_BTN_BORDER": "#4b5563",
}

THEMES = {"light": LIGHT, "dark": DARK}


def _prefs_path() -> str:
    try:
        from platformdirs import user_data_dir
        base = user_data_dir("MSK_DataCollector", appauthor=False)
    except ImportError:
        if os.name == "nt":
            base = os.path.join(
                os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                "MSK_DataCollector",
            )
        else:
            base = os.path.join(os.path.expanduser("~"), ".local", "share", "MSK_DataCollector")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "ui_prefs.json")


def load_theme_name() -> str:
    try:
        with open(_prefs_path(), "r") as f:
            return json.load(f).get("theme", "light")
    except Exception:
        return "light"


def save_theme_name(name: str) -> None:
    try:
        with open(_prefs_path(), "w") as f:
            json.dump({"theme": name}, f)
    except Exception:
        pass


def get_palette(name: str) -> dict:
    return THEMES.get(name, LIGHT)
