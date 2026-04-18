"""
Tab 2 — Structure Visibility
All items rated on a symmetric 5-point Likert scale.
1 = Not visible  →  5 = Fully visible
"""
import customtkinter as ctk

from ui.theme import LIGHT

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


class StructureTab(ctk.CTkFrame):
    def __init__(self, parent, on_change_callback=None, on_next_tab=None,
                 items=None, palette=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change_callback = on_change_callback
        self.on_next_tab = on_next_tab
        self._items = items or STRUCTURE_ITEMS
        self.palette = palette or LIGHT
        self._vars = {}
        self._buttons = {}
        self._themed_labels = []
        self._next_btn = None
        self._build()

    def _themed_label(self, parent, text, color_key, **kwargs):
        lbl = ctk.CTkLabel(parent, text=text, text_color=self.palette[color_key], **kwargs)
        self._themed_labels.append((lbl, color_key))
        return lbl

    def _build(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)

        self._themed_label(
            self._scroll, "Structure Visibility", "TAB_TEXT_HEADER",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, columnspan=6, pady=(12, 2), padx=16, sticky="w")

        self._themed_label(
            self._scroll, "1 = Not visible     5 = Fully visible",
            "TAB_TEXT_HINT", font=ctk.CTkFont(size=11),
        ).grid(row=1, column=0, columnspan=6, pady=(0, 8), padx=16, sticky="w")

        col_labels = ["", "1\nNot Visible", "2\nPoor", "3\nAdequate", "4\nGood", "5\nFull"]
        for col, label in enumerate(col_labels):
            self._themed_label(
                self._scroll, label, "TAB_TEXT_HINT",
                font=ctk.CTkFont(size=10, weight="bold"),
                width=80, justify="center",
            ).grid(row=2, column=col, padx=4, pady=(0, 4))

        for row_idx, (key, label) in enumerate(self._items):
            var = ctk.IntVar(value=0)
            self._vars[key] = var
            self._buttons[key] = []

            row = row_idx + 3

            self._themed_label(
                self._scroll, label, "TAB_TEXT_LABEL",
                anchor="w", width=190,
                font=ctk.CTkFont(size=13),
            ).grid(row=row, column=0, padx=(16, 8), pady=3, sticky="w")

            for score in range(1, 6):
                btn = ctk.CTkButton(
                    self._scroll,
                    text=str(score),
                    width=70, height=34,
                    fg_color=self.palette["TAB_BTN_UNSELECTED"],
                    hover_color=self.palette["TAB_BTN_HOVER"],
                    text_color=self.palette["TAB_TEXT_UNSELECTED"],
                    border_width=1,
                    border_color=self.palette["TAB_BTN_BORDER"],
                    command=lambda k=key, s=score: self._select(k, s),
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
                btn.grid(row=row, column=score, padx=3, pady=3)
                self._buttons[key].append(btn)

        if self.on_next_tab:
            self._next_btn = ctk.CTkButton(
                self._scroll, text="Next →", width=90, height=28,
                command=self.on_next_tab,
                fg_color=self.palette["BTN_BLUE"], text_color="white",
                font=ctk.CTkFont(size=11),
            )
            self._next_btn.grid(row=len(self._items) + 3, column=0, columnspan=6,
                                sticky="e", padx=8, pady=(12, 4))

    def _select(self, key: str, score: int):
        self._vars[key].set(score)
        p = self.palette
        for i, btn in enumerate(self._buttons[key]):
            if i + 1 == score:
                btn.configure(fg_color=p["TAB_BTN_SELECTED"], text_color=p["TAB_TEXT_SELECTED"],
                              border_color=p["TAB_BTN_SELECTED"])
            else:
                btn.configure(fg_color=p["TAB_BTN_UNSELECTED"], text_color=p["TAB_TEXT_UNSELECTED"],
                              border_color=p["TAB_BTN_BORDER"])
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
        p = self.palette
        for btn in self._buttons[key]:
            btn.configure(fg_color=p["TAB_BTN_UNSELECTED"], text_color=p["TAB_TEXT_UNSELECTED"],
                          border_color=p["TAB_BTN_BORDER"])

    def clear_all(self):
        for key in self._vars:
            self._clear_key(key)

    def unanswered_fields(self) -> list[str]:
        return [label for key, label in self._items if self._vars[key].get() == 0]

    def is_complete(self) -> bool:
        return all(var.get() != 0 for var in self._vars.values())

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
        if self._next_btn is not None:
            self._next_btn.configure(fg_color=palette["BTN_BLUE"])
