"""
Main application window.
Handles navigation, save logic, validation, and clipboard notifications.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

from data.excel_handler import ExcelHandler
from utils.clipboard import copy_to_clipboard
from ui.quality_tab import QualityTab
from ui.structure_tab import StructureTab
from ui.pathology_tab import PathologyTab
from ui.theme import LIGHT, DARK, get_palette, load_theme_name, save_theme_name


class MainWindow(ctk.CTk):
    def __init__(self, config=None):
        super().__init__()
        self._config = config
        title = config.window_title if config else "MSK Data Collector"
        self.title(title)
        self.geometry("820x620")
        self.minsize(560, 540)

        self._theme_name = load_theme_name()
        self.palette = get_palette(self._theme_name)
        ctk.set_appearance_mode("Dark" if self._theme_name == "dark" else "Light")

        answer_cols = config.answer_columns if config else None
        input_sheet = config.input_sheet_name if config else None
        output_sheet = config.output_sheet_name if config else None
        self.excel = ExcelHandler(
            answer_columns=answer_cols,
            input_sheet_name=input_sheet,
            output_sheet_name=output_sheet,
        )
        self.accessions: list[str] = []
        self.current_index: int = 0
        self._clipboard_after_id = None
        self._filter_incomplete = True

        # Widget → (prop, palette_key) registry for runtime re-theming.
        self._themed_widgets: list = []

        self._build_ui()
        self._set_loaded(False)

    def _register_themed(self, widget, prop: str, palette_key: str):
        self._themed_widgets.append((widget, prop, palette_key))

    # ------------------------------------------------------------------ #
    #  UI Construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        p = self.palette
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Top bar ──────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, corner_radius=0, fg_color=p["BG_TOP"])
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)
        self._register_themed(top, "fg_color", "BG_TOP")

        self.btn_open = ctk.CTkButton(
            top, text="Open Excel File", command=self._open_file,
            width=140, text_color="white", fg_color=p["BTN_BLUE"],
        )
        self.btn_open.grid(row=0, column=0, padx=12, pady=10)
        self._register_themed(self.btn_open, "fg_color", "BTN_BLUE")

        acc_frame = ctk.CTkFrame(top, fg_color="transparent")
        acc_frame.grid(row=0, column=1, padx=8, sticky="ew")

        lbl_accession_prefix = ctk.CTkLabel(
            acc_frame, text="Accession:",
            font=ctk.CTkFont(size=12), text_color=p["TEXT_GRAY"],
        )
        lbl_accession_prefix.pack(side="left")
        self._register_themed(lbl_accession_prefix, "text_color", "TEXT_GRAY")

        self.lbl_accession = ctk.CTkLabel(
            acc_frame, text="—",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=p["TEXT_MAIN"],
        )
        self.lbl_accession.pack(side="left", padx=(6, 0))
        self._register_themed(self.lbl_accession, "text_color", "TEXT_MAIN")

        self.lbl_clipboard = ctk.CTkLabel(
            acc_frame, text="",
            font=ctk.CTkFont(size=11),
            text_color=p["TEXT_GREEN"],
        )
        self.lbl_clipboard.pack(side="left", padx=(10, 0))
        self._register_themed(self.lbl_clipboard, "text_color", "TEXT_GREEN")

        # Right side of top bar: theme switch + jump-to
        right_frame = ctk.CTkFrame(top, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=8, pady=10)

        self.switch_theme = ctk.CTkSwitch(
            right_frame, text="Dark mode",
            command=self._toggle_theme,
            font=ctk.CTkFont(size=11),
            text_color=p["TEXT_MAIN"],
        )
        self.switch_theme.pack(side="left", padx=(0, 12))
        if self._theme_name == "dark":
            self.switch_theme.select()
        self._register_themed(self.switch_theme, "text_color", "TEXT_MAIN")

        lbl_jump = ctk.CTkLabel(
            right_frame, text="Jump to:",
            font=ctk.CTkFont(size=11), text_color=p["TEXT_GRAY"],
        )
        lbl_jump.pack(side="left")
        self._register_themed(lbl_jump, "text_color", "TEXT_GRAY")

        self.entry_jump = ctk.CTkEntry(
            right_frame, width=100, placeholder_text="accession",
            text_color=p["TEXT_MAIN"],
        )
        self.entry_jump.pack(side="left", padx=4)
        self.entry_jump.bind("<Return>", lambda e: self._jump_to())
        self._register_themed(self.entry_jump, "text_color", "TEXT_MAIN")

        self.btn_go = ctk.CTkButton(
            right_frame, text="Go", width=40, command=self._jump_to,
            text_color="white", fg_color=p["BTN_BLUE"],
        )
        self.btn_go.pack(side="left")
        self._register_themed(self.btn_go, "fg_color", "BTN_BLUE")

        # ── Progress bar row ─────────────────────────────────────────────
        prog_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=p["BG_PROG"])
        prog_frame.grid(row=1, column=0, sticky="ew")
        prog_frame.grid_columnconfigure(1, weight=1)
        self._register_themed(prog_frame, "fg_color", "BG_PROG")

        self.lbl_progress = ctk.CTkLabel(
            prog_frame, text="No file loaded",
            font=ctk.CTkFont(size=11), text_color=p["TEXT_GRAY"],
        )
        self.lbl_progress.grid(row=0, column=0, padx=12, pady=6, sticky="w")
        self._register_themed(self.lbl_progress, "text_color", "TEXT_GRAY")

        self.progress_bar = ctk.CTkProgressBar(prog_frame, height=8)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=12, pady=6, sticky="ew")

        self.cb_filter = ctk.CTkCheckBox(
            prog_frame, text="Show incomplete only",
            command=self._toggle_filter,
            font=ctk.CTkFont(size=11),
            text_color=p["TEXT_MAIN"],
        )
        self.cb_filter.grid(row=0, column=2, padx=12, pady=6)
        self.cb_filter.select()
        self._register_themed(self.cb_filter, "text_color", "TEXT_MAIN")

        self.lbl_save_path = ctk.CTkLabel(
            prog_frame, text="",
            font=ctk.CTkFont(size=10), text_color=p["TEXT_GRAY"],
        )
        self.lbl_save_path.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 4), sticky="w")
        self._register_themed(self.lbl_save_path, "text_color", "TEXT_GRAY")

        # ── Tab view ─────────────────────────────────────────────────────
        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 0))

        self.tab_view.add("Quality")
        self.tab_view.add("Structures")
        self.tab_view.add("Pathology")

        q_kwargs = {"items": self._config.quality_items} if self._config else {}
        self.quality_tab = QualityTab(
            self.tab_view.tab("Quality"),
            on_change_callback=self._on_answer_change,
            on_next_tab=lambda: self.tab_view.set("Structures"),
            palette=self.palette,
            **q_kwargs,
        )
        self.quality_tab.pack(fill="both", expand=True)

        s_kwargs = {"items": self._config.structure_items} if self._config else {}
        self.structure_tab = StructureTab(
            self.tab_view.tab("Structures"),
            on_change_callback=self._on_answer_change,
            on_next_tab=lambda: self.tab_view.set("Pathology"),
            palette=self.palette,
            **s_kwargs,
        )
        self.structure_tab.pack(fill="both", expand=True)

        p_kwargs = {}
        if self._config:
            p_kwargs = {
                "items": self._config.pathology_items,
                "encode": self._config.pathology_encode,
                "decode": self._config.pathology_decode,
                "choice_colors": self._config.pathology_choice_colors,
            }
        self.pathology_tab = PathologyTab(
            self.tab_view.tab("Pathology"),
            on_change_callback=self._on_answer_change,
            palette=self.palette,
            **p_kwargs,
        )
        self.pathology_tab.pack(fill="both", expand=True)

        # ── Notes row ────────────────────────────────────────────────────
        notes_frame = ctk.CTkFrame(self, fg_color="transparent")
        notes_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 0))
        notes_frame.grid_columnconfigure(1, weight=1)

        lbl_notes = ctk.CTkLabel(
            notes_frame, text="Notes:",
            font=ctk.CTkFont(size=12), text_color=p["TEXT_MAIN"],
        )
        lbl_notes.grid(row=0, column=0, padx=(0, 8), sticky="w")
        self._register_themed(lbl_notes, "text_color", "TEXT_MAIN")

        self.entry_notes = ctk.CTkEntry(
            notes_frame,
            placeholder_text="Optional notes for this record",
            text_color=p["TEXT_MAIN"],
        )
        self.entry_notes.grid(row=0, column=1, sticky="ew")
        self._register_themed(self.entry_notes, "text_color", "TEXT_MAIN")

        # ── Bottom action bar (grid, not pack) ───────────────────────────
        bottom = ctk.CTkFrame(self, corner_radius=0, fg_color=p["BG_BOTTOM"])
        bottom.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        bottom.grid_columnconfigure(2, weight=1)   # spacer absorbs slack
        self._register_themed(bottom, "fg_color", "BG_BOTTOM")

        self.btn_prev_patient = ctk.CTkButton(
            bottom, text="◀  Prev Patient", width=130,
            command=self._go_previous_patient,
            fg_color=p["BTN_GRAY"], text_color="white",
        )
        self.btn_prev_patient.grid(row=0, column=0, padx=(12, 4), pady=10)
        self._register_themed(self.btn_prev_patient, "fg_color", "BTN_GRAY")

        self.btn_prev_incomplete = ctk.CTkButton(
            bottom, text="◀  Prev Incomplete", width=150,
            command=self._go_previous_incomplete,
            fg_color=p["BTN_GRAY"], text_color="white",
        )
        self.btn_prev_incomplete.grid(row=0, column=1, padx=4, pady=10)
        self._register_themed(self.btn_prev_incomplete, "fg_color", "BTN_GRAY")

        self.lbl_save_status = ctk.CTkLabel(
            bottom, text="",
            font=ctk.CTkFont(size=11),
            text_color=p["TEXT_GREEN"],
        )
        self.lbl_save_status.grid(row=0, column=2, padx=16, sticky="w")
        self._register_themed(self.lbl_save_status, "text_color", "TEXT_GREEN")

        self.btn_save = ctk.CTkButton(
            bottom, text="Save", width=90,
            command=self._save,
            fg_color=p["BTN_GREEN"], text_color="white",
        )
        self.btn_save.grid(row=0, column=3, padx=4, pady=10)
        self._register_themed(self.btn_save, "fg_color", "BTN_GREEN")

        self.btn_save_exit = ctk.CTkButton(
            bottom, text="Save & Exit", width=120,
            command=self._save_and_exit,
            fg_color=p["BTN_GRAY"], text_color="white",
        )
        self.btn_save_exit.grid(row=0, column=4, padx=4, pady=10)
        self._register_themed(self.btn_save_exit, "fg_color", "BTN_GRAY")

        self.btn_save_next = ctk.CTkButton(
            bottom, text="Save & Next Patient  ▶", width=190,
            command=self._save_and_next,
            fg_color=p["BTN_BLUE"], text_color="white",
        )
        self.btn_save_next.grid(row=0, column=5, padx=(4, 12), pady=10)
        self._register_themed(self.btn_save_next, "fg_color", "BTN_BLUE")

        # Responsive bottom-bar labels: (button, wide_text, wide_w, short_text, short_w)
        self._responsive_buttons = [
            (self.btn_prev_patient,    "\u25c0  Prev Patient",         130, "\u25c0 Prev", 80),
            (self.btn_prev_incomplete, "\u25c0  Prev Incomplete",      150, "\u25c0\u25c0",    50),
            (self.btn_save_exit,       "Save & Exit",                  120, "Exit",        70),
            (self.btn_save_next,       "Save & Next Patient  \u25b6",  190, "Next \u25b6",  80),
        ]
        self._compact_mode = False
        self.bind("<Configure>", self._on_window_configure, add="+")

        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._save_and_next())
        self.bind("<Left>",   lambda e: self._go_previous_incomplete())
        self.bind("<Right>",  lambda e: self._save_and_next())

    # ------------------------------------------------------------------ #
    #  Responsive bottom bar                                               #
    # ------------------------------------------------------------------ #

    def _on_window_configure(self, event):
        # str() comparison: tkinter may leave event.widget as the Tcl path "."
        # on Windows/CTk when _nametowidget can't resolve it to the Python self.
        if str(event.widget) != str(self):
            return
        width = event.width
        # Hysteresis prevents flicker when dragged exactly on the boundary.
        if not self._compact_mode and width < 780:
            self._compact_mode = True
            self._apply_button_mode()
        elif self._compact_mode and width >= 820:
            self._compact_mode = False
            self._apply_button_mode()

    def _apply_button_mode(self):
        for btn, wide_text, wide_w, short_text, short_w in self._responsive_buttons:
            if self._compact_mode:
                btn.configure(text=short_text, width=short_w)
            else:
                btn.configure(text=wide_text, width=wide_w)

    # ------------------------------------------------------------------ #
    #  Theme switching                                                     #
    # ------------------------------------------------------------------ #

    def _toggle_theme(self):
        self._theme_name = "dark" if self.switch_theme.get() else "light"
        save_theme_name(self._theme_name)
        self.palette = get_palette(self._theme_name)
        ctk.set_appearance_mode("Dark" if self._theme_name == "dark" else "Light")
        self._apply_theme()

    def _apply_theme(self):
        p = self.palette
        for widget, prop, key in self._themed_widgets:
            try:
                widget.configure(**{prop: p[key]})
            except Exception:
                pass
        self.quality_tab.apply_theme(p)
        self.structure_tab.apply_theme(p)
        self.pathology_tab.apply_theme(p)

    # ------------------------------------------------------------------ #
    #  File Loading                                                        #
    # ------------------------------------------------------------------ #

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            self.accessions = self.excel.load(path)
            statuses = self.excel.get_completion_status()
            first_incomplete = next(
                (i for i in range(len(self.accessions))
                 if statuses.get(i, "incomplete") not in ("complete", "skipped")),
                0
            )
            self.current_index = first_incomplete
            self._set_loaded(True)
            self._load_record(self.current_index)
            out_path = self.excel.get_output_path()
            self.lbl_save_path.configure(text=f"Scores saving to: {out_path}")
        except Exception as e:
            messagebox.showerror("Error loading file", str(e))

    def _set_loaded(self, loaded: bool):
        state = "normal" if loaded else "disabled"
        for widget in (self.btn_prev_patient, self.btn_prev_incomplete, self.btn_save,
                       self.btn_save_next, self.btn_save_exit, self.entry_notes, self.cb_filter):
            widget.configure(state=state)

    # ------------------------------------------------------------------ #
    #  Record Navigation                                                   #
    # ------------------------------------------------------------------ #

    def _load_record(self, index: int):
        if not self.accessions:
            return
        self.current_index = index
        accession = self.excel.get_accession(index)

        self.lbl_accession.configure(text=accession)

        msg = copy_to_clipboard(accession)
        self.lbl_clipboard.configure(text=msg)
        if self._clipboard_after_id:
            self.after_cancel(self._clipboard_after_id)
        self._clipboard_after_id = self.after(
            3000, lambda: self.lbl_clipboard.configure(text="")
        )

        data = self.excel.read_row(index)
        self.quality_tab.set_values(data)
        self.structure_tab.set_values(data)
        self.pathology_tab.set_values(data)

        notes = data.get("notes") or ""
        self.entry_notes.delete(0, "end")
        self.entry_notes.insert(0, str(notes) if notes else "")

        self.tab_view.set("Quality")
        self._update_progress()
        self._update_tab_labels()
        self.lbl_save_status.configure(text="")
        prev_enabled = "normal" if index > 0 else "disabled"
        self.btn_prev_patient.configure(state=prev_enabled)
        self.btn_prev_incomplete.configure(state=prev_enabled)

        if self.excel.has_partial_answers(index):
            messagebox.showinfo(
                "Previously incomplete",
                "This patient was previously started but not completed.\n"
                "Your earlier selections have been restored — you can continue where you left off.",
            )

    def _go_previous_patient(self):
        if self.current_index > 0:
            self._load_record(self.current_index - 1)

    def _go_previous_incomplete(self):
        if self.current_index > 0:
            prev_idx = self.current_index - 1
            if self._filter_incomplete:
                statuses = self.excel.get_completion_status()
                while prev_idx >= 0:
                    if statuses.get(prev_idx, "incomplete") not in ("complete", "skipped"):
                        break
                    prev_idx -= 1
                else:
                    return
            self._load_record(prev_idx)

    def _go_next(self):
        if self.current_index < self.excel.total_records() - 1:
            next_idx = self.current_index + 1
            if self._filter_incomplete:
                statuses = self.excel.get_completion_status()
                while next_idx < self.excel.total_records():
                    if statuses.get(next_idx, "incomplete") not in ("complete", "skipped"):
                        break
                    next_idx += 1
                else:
                    messagebox.showinfo("All done!", "All records have been completed.")
                    return
            self._load_record(next_idx)
        else:
            messagebox.showinfo("End of records", "You have reached the last record.")

    def _jump_to(self):
        query = self.entry_jump.get().strip()
        if not query:
            return
        for i, acc in enumerate(self.accessions):
            if str(acc).strip() == query:
                self._load_record(i)
                self.entry_jump.delete(0, "end")
                return
        messagebox.showwarning("Not found", f"Accession '{query}' not found.")

    def _toggle_filter(self):
        self._filter_incomplete = bool(self.cb_filter.get())

    # ------------------------------------------------------------------ #
    #  Save Logic                                                          #
    # ------------------------------------------------------------------ #

    def _collect_answers(self) -> dict:
        answers = {}
        answers.update(self.quality_tab.get_values())
        answers.update(self.structure_tab.get_values())
        answers.update(self.pathology_tab.get_values())
        answers["notes"] = self.entry_notes.get().strip() or None
        answers["saved_at"] = datetime.now().isoformat(timespec="seconds")
        return answers

    def _validate(self) -> list[str]:
        missing = []
        missing += self.quality_tab.unanswered_fields()
        missing += self.structure_tab.unanswered_fields()
        missing += self.pathology_tab.unanswered_fields()
        return missing

    def _save(self, mark_complete=True) -> bool:
        if not self.accessions:
            return False

        missing = self._validate()
        if missing:
            msg = (
                f"{len(missing)} question(s) unanswered:\n  • "
                + "\n  • ".join(missing)
                + "\n\nSave anyway?"
            )
            if not messagebox.askyesno("Incomplete answers", msg,
                                       icon="warning", default="no"):
                return False

        answers = self._collect_answers()
        all_answered = len(self._validate()) == 0
        answers["status"] = "complete" if (mark_complete and all_answered) else "incomplete"

        try:
            self.excel.write_row(self.current_index, answers)
            timestamp = datetime.now().strftime("%I:%M %p")
            self.lbl_save_status.configure(
                text=f"✓ Saved — {timestamp}",
            )
            self._update_tab_labels()
            self._update_progress()
            return True
        except Exception as e:
            messagebox.showerror("Save error", str(e))
            return False

    def _save_and_next(self):
        if self._save():
            self._go_next()

    def _save_and_exit(self):
        if self._save(mark_complete=False):
            self.destroy()

    # ------------------------------------------------------------------ #
    #  UI Updates                                                          #
    # ------------------------------------------------------------------ #

    def _on_answer_change(self):
        self._update_tab_labels()

    def _update_tab_labels(self):
        q = "Quality ✓" if self.quality_tab.is_complete() else "Quality"
        s = "Structures ✓" if self.structure_tab.is_complete() else "Structures"
        p = "Pathology ✓" if self.pathology_tab.is_complete() else "Pathology"
        base = self._config.window_title if self._config else "MSK Data Collector"
        self.title(f"{base}  |  [{q}]  [{s}]  [{p}]")

    def _update_progress(self):
        total = self.excel.total_records()
        if total == 0:
            return
        statuses = self.excel.get_completion_status()
        done = sum(1 for s in statuses.values() if s in ("complete", "skipped"))
        pct = done / total
        self.progress_bar.set(pct)
        self.lbl_progress.configure(
            text=f"Record {self.current_index + 1} of {total}  —  "
                 f"{done} completed ({int(pct * 100)}%)"
        )
