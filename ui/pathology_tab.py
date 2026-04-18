"""
Tab 3 — Pathology
Most items: Yes / No
Articular cartilage defect: None / Partial Thickness / Full Thickness
"""
import customtkinter as ctk

from ui.theme import LIGHT

PATHOLOGY_ITEMS = [
    ("acl_tear",                  "ACL Tear",                      ["No", "Yes"]),
    ("pcl_tear",                  "PCL Tear",                      ["No", "Yes"]),
    ("mcl_tear",                  "MCL Tear",                      ["No", "Yes"]),
    ("lcl_tear",                  "LCL Tear",                      ["No", "Yes"]),
    ("medial_meniscus_tear",      "Medial Meniscus Tear",          ["No", "Yes"]),
    ("lateral_meniscus_tear",     "Lateral Meniscus Tear",         ["No", "Yes"]),
    ("articular_cartilage_defect","Articular Cartilage Defect",    ["None", "Partial Thickness", "Full Thickness"]),
    ("bone_marrow_edema",         "Bone Marrow Edema",             ["No", "Yes"]),
]

# String label → integer written to Excel
_ENCODE = {
    "Yes": 1, "No": 0,
    "None": 0, "Partial Thickness": 1, "Full Thickness": 2,
}

# Tuple-of-choices → {int: string label} for round-trip decode
_DECODE = {
    ("No", "Yes"):                                   {1: "Yes", 0: "No"},
    ("None", "Partial Thickness", "Full Thickness"): {0: "None", 1: "Partial Thickness", 2: "Full Thickness"},
}

# Pathology colors carry clinical meaning — kept constant across themes.
CHOICE_ACTIVE = {
    "Yes":              ("#c0392b", "#ffffff"),
    "No":               ("#27ae60", "#ffffff"),
    "None":             ("#27ae60", "#ffffff"),
    "Partial Thickness":("#e67e22", "#ffffff"),
    "Full Thickness":   ("#c0392b", "#ffffff"),
}


class PathologyTab(ctk.CTkFrame):
    def __init__(self, parent, on_change_callback=None, items=None,
                 encode=None, decode=None, choice_colors=None, palette=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change_callback = on_change_callback
        self._items = items or PATHOLOGY_ITEMS
        self._encode = encode or _ENCODE
        self._decode = decode or _DECODE
        self._choice_colors = choice_colors or CHOICE_ACTIVE
        self.palette = palette or LIGHT
        self._vars = {}
        self._buttons = {}
        self._themed_labels = []
        self._build()

    def _themed_label(self, parent, text, color_key, **kwargs):
        lbl = ctk.CTkLabel(parent, text=text, text_color=self.palette[color_key], **kwargs)
        self._themed_labels.append((lbl, color_key))
        return lbl

    def _build(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)

        self._themed_label(
            self._scroll, "Pathology", "TAB_TEXT_HEADER",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(12, 2), padx=16, sticky="w")

        self._themed_label(
            self._scroll, "Select the finding for each structure.",
            "TAB_TEXT_HINT", font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=2, pady=(0, 8), padx=16, sticky="w")

        for row_idx, (key, label, choices) in enumerate(self._items):
            var = ctk.StringVar(value="")
            self._vars[key] = var
            self._buttons[key] = {}

            row = row_idx + 2

            self._themed_label(
                self._scroll, label, "TAB_TEXT_LABEL",
                anchor="w", width=210, font=ctk.CTkFont(size=13),
            ).grid(row=row, column=0, padx=(16, 12), pady=5, sticky="w")

            btn_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            btn_frame.grid(row=row, column=1, padx=4, pady=5, sticky="w")

            btn_width = 130 if len(choices) > 2 else 90

            for choice in choices:
                btn = ctk.CTkButton(
                    btn_frame,
                    text=choice,
                    width=btn_width, height=34,
                    fg_color=self.palette["TAB_BTN_UNSELECTED"],
                    hover_color=self.palette["TAB_BTN_HOVER"],
                    text_color=self.palette["TAB_TEXT_UNSELECTED"],
                    border_width=1,
                    border_color=self.palette["TAB_BTN_BORDER"],
                    command=lambda k=key, c=choice: self._select(k, c),
                    font=ctk.CTkFont(size=13),
                )
                btn.pack(side="left", padx=4)
                self._buttons[key][choice] = btn

    def _select(self, key: str, choice: str):
        self._vars[key].set(choice)
        p = self.palette
        item = next(item for item in self._items if item[0] == key)
        for c in item[2]:
            btn = self._buttons[key][c]
            if c == choice:
                bg, fg = self._choice_colors.get(c, (p["BTN_BLUE"], "#ffffff"))
                btn.configure(fg_color=bg, text_color=fg, border_color=bg)
            else:
                btn.configure(fg_color=p["TAB_BTN_UNSELECTED"], text_color=p["TAB_TEXT_UNSELECTED"],
                              border_color=p["TAB_BTN_BORDER"])
        if self.on_change_callback:
            self.on_change_callback()

    def get_values(self) -> dict:
        return {key: (self._encode[var.get()] if var.get() != "" else None)
                for key, var in self._vars.items()}

    def set_values(self, data: dict):
        for key, _, choices in self._items:
            val = data.get(key)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                self._clear_key(key)
                continue
            try:
                choice = self._decode.get(tuple(choices), {}).get(int(val))
            except (ValueError, TypeError):
                choice = None
            if choice is None and str(val) in choices:
                choice = str(val)
            if choice:
                self._select(key, choice)
            else:
                self._clear_key(key)

    def _clear_key(self, key: str):
        self._vars[key].set("")
        p = self.palette
        for btn in self._buttons[key].values():
            btn.configure(fg_color=p["TAB_BTN_UNSELECTED"], text_color=p["TAB_TEXT_UNSELECTED"],
                          border_color=p["TAB_BTN_BORDER"])

    def clear_all(self):
        for key in self._vars:
            self._clear_key(key)

    def unanswered_fields(self) -> list[str]:
        return [label for key, label, _ in self._items if self._vars[key].get() == ""]

    def is_complete(self) -> bool:
        return all(var.get() != "" for var in self._vars.values())

    def apply_theme(self, palette: dict) -> None:
        self.palette = palette
        for widget, key in self._themed_labels:
            widget.configure(text_color=palette[key])
        for key in list(self._vars.keys()):
            val = self._vars[key].get()
            if val:
                self._select(key, val)
            else:
                self._clear_key(key)
