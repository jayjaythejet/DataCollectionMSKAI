"""
AppConfig dataclass and shared encoding helpers for body-part configs.
"""
from dataclasses import dataclass, field

# Master label → integer encoding
LABEL_ENCODE = {
    "Yes": 1, "No": 0,
    "None": 0, "Partial Thickness": 1, "Full Thickness": 2,
    "No Tear": 0, "Partial Tear": 1, "Full Thickness Tear": 2,
}

# Master label → (bg_color, text_color)
LABEL_COLORS = {
    "Yes":                ("#c0392b", "#ffffff"),
    "No":                 ("#27ae60", "#ffffff"),
    "None":               ("#27ae60", "#ffffff"),
    "Partial Thickness":  ("#e67e22", "#ffffff"),
    "Full Thickness":     ("#c0392b", "#ffffff"),
    "No Tear":            ("#27ae60", "#ffffff"),
    "Partial Tear":       ("#e67e22", "#ffffff"),
    "Full Thickness Tear":("#c0392b", "#ffffff"),
}


def build_pathology_maps(pathology_items):
    """
    Auto-generate encode, decode, and choice_colors dicts from pathology_items
    using the master LABEL_ENCODE and LABEL_COLORS mappings.
    """
    encode = {}
    decode = {}
    choice_colors = {}

    seen_choice_sets = set()
    for _key, _label, choices in pathology_items:
        choice_tuple = tuple(choices)
        for c in choices:
            if c not in encode:
                encode[c] = LABEL_ENCODE[c]
            if c not in choice_colors:
                choice_colors[c] = LABEL_COLORS[c]
        if choice_tuple not in seen_choice_sets:
            seen_choice_sets.add(choice_tuple)
            decode[choice_tuple] = {LABEL_ENCODE[c]: c for c in choices}

    return encode, decode, choice_colors


@dataclass
class AppConfig:
    app_title: str
    window_title: str
    quality_items: list       # list of (key, label)
    structure_items: list     # list of (key, label)
    pathology_items: list     # list of (key, label, choices)
    pathology_encode: dict = field(default_factory=dict)
    pathology_decode: dict = field(default_factory=dict)
    pathology_choice_colors: dict = field(default_factory=dict)

    def __post_init__(self):
        # Auto-generate pathology maps if not provided
        if not self.pathology_encode:
            enc, dec, colors = build_pathology_maps(self.pathology_items)
            self.pathology_encode = enc
            self.pathology_decode = dec
            self.pathology_choice_colors = colors

    @property
    def answer_columns(self) -> list[str]:
        cols = []
        for key, _label in self.quality_items:
            cols.append(key)
        for key, _label in self.structure_items:
            cols.append(key)
        for key, _label, _choices in self.pathology_items:
            cols.append(key)
        cols += ["notes", "status"]
        return cols
