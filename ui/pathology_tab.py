"""
Tab 3 — Pathology
Most items: Yes / No
Articular cartilage defect: None / Partial Thickness / Full Thickness
"""
import customtkinter as ctk

PATHOLOGY_ITEMS = [
    ("acl_tear",                  "ACL Tear",                      ["Yes", "No"]),
    ("pcl_tear",                  "PCL Tear",                      ["Yes", "No"]),
    ("mcl_tear",                  "MCL Tear",                      ["Yes", "No"]),
    ("lcl_tear",                  "LCL Tear",                      ["Yes", "No"]),
    ("medial_meniscus_tear",      "Medial Meniscus Tear",          ["Yes", "No"]),
    ("lateral_meniscus_tear",     "Lateral Meniscus Tear",         ["Yes", "No"]),
    ("articular_cartilage_defect","Articular Cartilage Defect",    ["None", "Partial Thickness", "Full Thickness"]),
    ("bone_marrow_edema",         "Bone Marrow Edema",             ["Yes", "No"]),
]

# String label → integer written to Excel
_ENCODE = {
    "Yes": 1, "No": 0,
    "None": 0, "Partial Thickness": 1, "Full Thickness": 2,
}

# Tuple-of-choices → {int: string label} for round-trip decode
_DECODE = {
    ("Yes", "No"):                                   {1: "Yes", 0: "No"},
    ("None", "Partial Thickness", "Full Thickness"): {0: "None", 1: "Partial Thickness", 2: "Full Thickness"},
}

# Colors per choice
CHOICE_ACTIVE = {
    "Yes":              ("#c0392b", "#ffffff"),  # (bg, text)
    "No":               ("#27ae60", "#ffffff"),
    "None":             ("#27ae60", "#ffffff"),
    "Partial Thickness":("#e67e22", "#ffffff"),
    "Full Thickness":   ("#c0392b", "#ffffff"),
}
BTN_UNSELECTED  = "#e0e5ea"
TEXT_UNSELECTED = "#111111"
TEXT_LABEL      = "#111111"
TEXT_HINT       = "#666666"
TEXT_HEADER     = "#111111"


class PathologyTab(ctk.CTkFrame):
    def __init__(self, parent, on_change_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change_callback = on_change_callback
        self._vars = {}
        self._buttons = {}
        self._build()

    def _build(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self._scroll,
            text="Pathology",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_HEADER,
        ).grid(row=0, column=0, columnspan=2, pady=(12, 2), padx=16, sticky="w")

        ctk.CTkLabel(
            self._scroll,
            text="Select the finding for each structure.",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_HINT,
        ).grid(row=1, column=0, columnspan=2, pady=(0, 8), padx=16, sticky="w")

        for row_idx, (key, label, choices) in enumerate(PATHOLOGY_ITEMS):
            var = ctk.StringVar(value="")
            self._vars[key] = var
            self._buttons[key] = {}

            row = row_idx + 2

            ctk.CTkLabel(
                self._scroll, text=label, anchor="w", width=210,
                font=ctk.CTkFont(size=13), text_color=TEXT_LABEL,
            ).grid(row=row, column=0, padx=(16, 12), pady=5, sticky="w")

            btn_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            btn_frame.grid(row=row, column=1, padx=4, pady=5, sticky="w")

            btn_width = 130 if len(choices) > 2 else 90

            for choice in choices:
                btn = ctk.CTkButton(
                    btn_frame,
                    text=choice,
                    width=btn_width, height=34,
                    fg_color=BTN_UNSELECTED,
                    hover_color="#c0ccd8",
                    text_color=TEXT_UNSELECTED,
                    border_width=1,
                    border_color="#aab0b8",
                    command=lambda k=key, c=choice: self._select(k, c),
                    font=ctk.CTkFont(size=13),
                )
                btn.pack(side="left", padx=4)
                self._buttons[key][choice] = btn

    def _select(self, key: str, choice: str):
        self._vars[key].set(choice)
        items = next(item for item in PATHOLOGY_ITEMS if item[0] == key)
        for c in items[2]:
            btn = self._buttons[key][c]
            if c == choice:
                bg, fg = CHOICE_ACTIVE.get(c, ("#1f6aa5", "#ffffff"))
                btn.configure(fg_color=bg, text_color=fg, border_color=bg)
            else:
                btn.configure(fg_color=BTN_UNSELECTED, text_color=TEXT_UNSELECTED,
                              border_color="#aab0b8")
        if self.on_change_callback:
            self.on_change_callback()

    def get_values(self) -> dict:
        return {key: (_ENCODE[var.get()] if var.get() != "" else None)
                for key, var in self._vars.items()}

    def set_values(self, data: dict):
        for key, _, choices in PATHOLOGY_ITEMS:
            val = data.get(key)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                self._clear_key(key)
                continue
            # Try numeric decode (new format)
            try:
                choice = _DECODE.get(tuple(choices), {}).get(int(val))
            except (ValueError, TypeError):
                choice = None
            # Fall back to direct string match (old format / backward compat)
            if choice is None and str(val) in choices:
                choice = str(val)
            if choice:
                self._select(key, choice)
            else:
                self._clear_key(key)

    def _clear_key(self, key: str):
        self._vars[key].set("")
        for btn in self._buttons[key].values():
            btn.configure(fg_color=BTN_UNSELECTED, text_color=TEXT_UNSELECTED,
                          border_color="#aab0b8")

    def clear_all(self):
        for key in self._vars:
            self._clear_key(key)

    def unanswered_fields(self) -> list[str]:
        return [label for key, label, _ in PATHOLOGY_ITEMS if self._vars[key].get() == ""]

    def is_complete(self) -> bool:
        return all(var.get() != "" for var in self._vars.values())
