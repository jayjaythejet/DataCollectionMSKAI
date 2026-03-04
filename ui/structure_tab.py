"""
Tab 2 — Structure Visibility
All items rated on a symmetric 5-point Likert scale.
1 = Not visible  →  5 = Fully visible
"""
import customtkinter as ctk

STRUCTURE_ITEMS = [
    ("acl_visibility",                 "ACL"),
    ("pcl_visibility",                 "PCL"),
    ("mcl_visibility",                 "MCL"),
    ("lcl_visibility",                 "LCL"),
    ("medial_meniscus_visibility",     "Medial Meniscus"),
    ("lateral_meniscus_visibility",    "Lateral Meniscus"),
    ("extensor_tendons_visibility",    "Extensor Tendons"),
    ("articular_cartilage_visibility", "Articular Cartilage"),
    ("bones_visibility",               "Bones"),
]

BTN_SELECTED    = "#1f6aa5"
BTN_UNSELECTED  = "#e0e5ea"
TEXT_SELECTED   = "#ffffff"
TEXT_UNSELECTED = "#111111"
TEXT_LABEL      = "#111111"
TEXT_HINT       = "#666666"
TEXT_HEADER     = "#111111"


class StructureTab(ctk.CTkFrame):
    def __init__(self, parent, on_change_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change_callback = on_change_callback
        self._vars = {}
        self._buttons = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Structure Visibility",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT_HEADER,
        ).grid(row=0, column=0, columnspan=6, pady=(12, 2), padx=16, sticky="w")

        ctk.CTkLabel(
            self,
            text="1 = Not visible     5 = Fully visible",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_HINT,
        ).grid(row=1, column=0, columnspan=6, pady=(0, 8), padx=16, sticky="w")

        col_labels = ["", "1\nNot Visible", "2\nPoor", "3\nAdequate", "4\nGood", "5\nFull"]
        for col, label in enumerate(col_labels):
            ctk.CTkLabel(
                self, text=label,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=TEXT_HINT, width=80, justify="center",
            ).grid(row=2, column=col, padx=4, pady=(0, 4))

        for row_idx, (key, label) in enumerate(STRUCTURE_ITEMS):
            var = ctk.IntVar(value=0)
            self._vars[key] = var
            self._buttons[key] = []

            row = row_idx + 3

            ctk.CTkLabel(
                self, text=label, anchor="w", width=190,
                font=ctk.CTkFont(size=13), text_color=TEXT_LABEL,
            ).grid(row=row, column=0, padx=(16, 8), pady=3, sticky="w")

            for score in range(1, 6):
                btn = ctk.CTkButton(
                    self,
                    text=str(score),
                    width=70, height=34,
                    fg_color=BTN_UNSELECTED,
                    hover_color="#c0ccd8",
                    text_color=TEXT_UNSELECTED,
                    border_width=1,
                    border_color="#aab0b8",
                    command=lambda k=key, s=score: self._select(k, s),
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
                btn.grid(row=row, column=score, padx=3, pady=3)
                self._buttons[key].append(btn)

    def _select(self, key: str, score: int):
        self._vars[key].set(score)
        for i, btn in enumerate(self._buttons[key]):
            if i + 1 == score:
                btn.configure(fg_color=BTN_SELECTED, text_color=TEXT_SELECTED,
                              border_color=BTN_SELECTED)
            else:
                btn.configure(fg_color=BTN_UNSELECTED, text_color=TEXT_UNSELECTED,
                              border_color="#aab0b8")
        if self.on_change_callback:
            self.on_change_callback()

    def get_values(self) -> dict:
        return {key: (var.get() if var.get() != 0 else None)
                for key, var in self._vars.items()}

    def set_values(self, data: dict):
        for key in self._vars:
            val = data.get(key)
            if val is not None:
                try:
                    self._select(key, int(val))
                except (ValueError, TypeError):
                    self._clear_key(key)
            else:
                self._clear_key(key)

    def _clear_key(self, key: str):
        self._vars[key].set(0)
        for btn in self._buttons[key]:
            btn.configure(fg_color=BTN_UNSELECTED, text_color=TEXT_UNSELECTED,
                          border_color="#aab0b8")

    def clear_all(self):
        for key in self._vars:
            self._clear_key(key)

    def unanswered_fields(self) -> list[str]:
        return [label for key, label in STRUCTURE_ITEMS if self._vars[key].get() == 0]

    def is_complete(self) -> bool:
        return all(var.get() != 0 for var in self._vars.values())
