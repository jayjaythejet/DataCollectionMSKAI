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

# Colors (explicit — no tuples to avoid macOS rendering issues)
BG_TOP     = "#dde3ea"
BG_PROG    = "#cdd3da"
BG_BOTTOM  = "#dde3ea"
TEXT_MAIN  = "#111111"
TEXT_GRAY  = "#555555"
TEXT_GREEN = "#2e7d32"
TEXT_AMBER = "#b45000"
BTN_BLUE   = "#1f6aa5"
BTN_GRAY   = "#888888"
BTN_GREEN  = "#2e7d32"
BTN_ORANGE = "#c07000"


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MSK Data Collector")
        self.geometry("720x620")
        self.minsize(680, 540)

        self.excel = ExcelHandler()
        self.accessions: list[str] = []
        self.current_index: int = 0
        self._clipboard_after_id = None
        self._filter_incomplete = False

        self._build_ui()
        self._set_loaded(False)

    # ------------------------------------------------------------------ #
    #  UI Construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Top bar ──────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_TOP)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        self.btn_open = ctk.CTkButton(
            top, text="Open Excel File", command=self._open_file,
            width=140, text_color="white", fg_color=BTN_BLUE,
        )
        self.btn_open.grid(row=0, column=0, padx=12, pady=10)

        # Accession display
        acc_frame = ctk.CTkFrame(top, fg_color="transparent")
        acc_frame.grid(row=0, column=1, padx=8, sticky="ew")

        ctk.CTkLabel(acc_frame, text="Accession:",
                     font=ctk.CTkFont(size=12), text_color=TEXT_GRAY).pack(side="left")
        self.lbl_accession = ctk.CTkLabel(
            acc_frame, text="—",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_MAIN,
        )
        self.lbl_accession.pack(side="left", padx=(6, 0))

        self.lbl_clipboard = ctk.CTkLabel(
            acc_frame, text="",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_GREEN,
        )
        self.lbl_clipboard.pack(side="left", padx=(10, 0))

        # Jump-to search
        jump_frame = ctk.CTkFrame(top, fg_color="transparent")
        jump_frame.grid(row=0, column=2, padx=8, pady=10)

        ctk.CTkLabel(jump_frame, text="Jump to:",
                     font=ctk.CTkFont(size=11), text_color=TEXT_GRAY).pack(side="left")
        self.entry_jump = ctk.CTkEntry(
            jump_frame, width=100, placeholder_text="accession",
            text_color=TEXT_MAIN,
        )
        self.entry_jump.pack(side="left", padx=4)
        self.entry_jump.bind("<Return>", lambda e: self._jump_to())
        ctk.CTkButton(
            jump_frame, text="Go", width=40, command=self._jump_to,
            text_color="white", fg_color=BTN_BLUE,
        ).pack(side="left")

        # Theme toggle
        self._dark_mode = False
        self.btn_theme = ctk.CTkButton(
            top, text="Dark Mode", width=100,
            command=self._toggle_theme,
            fg_color=BTN_GRAY, text_color="white",
        )
        self.btn_theme.grid(row=0, column=3, padx=8, pady=10)

        # ── Progress bar row ─────────────────────────────────────────────
        prog_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_PROG)
        prog_frame.grid(row=1, column=0, sticky="ew")
        prog_frame.grid_columnconfigure(1, weight=1)

        self.lbl_progress = ctk.CTkLabel(
            prog_frame, text="No file loaded",
            font=ctk.CTkFont(size=11), text_color=TEXT_GRAY,
        )
        self.lbl_progress.grid(row=0, column=0, padx=12, pady=6, sticky="w")

        self.progress_bar = ctk.CTkProgressBar(prog_frame, height=8)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=1, padx=12, pady=6, sticky="ew")

        self.cb_filter = ctk.CTkCheckBox(
            prog_frame, text="Show incomplete only",
            command=self._toggle_filter,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MAIN,
        )
        self.cb_filter.grid(row=0, column=2, padx=12, pady=6)

        self.lbl_save_path = ctk.CTkLabel(
            prog_frame, text="",
            font=ctk.CTkFont(size=10), text_color=TEXT_GRAY,
        )
        self.lbl_save_path.grid(row=1, column=0, columnspan=3, padx=12, pady=(0, 4), sticky="w")

        # ── Tab view ─────────────────────────────────────────────────────
        self.tab_view = ctk.CTkTabview(self, anchor="nw")
        self.tab_view.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 0))

        self.tab_view.add("Quality")
        self.tab_view.add("Structures")
        self.tab_view.add("Pathology")

        self.quality_tab = QualityTab(
            self.tab_view.tab("Quality"),
            on_change_callback=self._on_answer_change,
        )
        self.quality_tab.pack(fill="both", expand=True)

        self.structure_tab = StructureTab(
            self.tab_view.tab("Structures"),
            on_change_callback=self._on_answer_change,
        )
        self.structure_tab.pack(fill="both", expand=True)

        self.pathology_tab = PathologyTab(
            self.tab_view.tab("Pathology"),
            on_change_callback=self._on_answer_change,
        )
        self.pathology_tab.pack(fill="both", expand=True)

        # ── Notes row ────────────────────────────────────────────────────
        notes_frame = ctk.CTkFrame(self, fg_color="transparent")
        notes_frame.grid(row=3, column=0, sticky="ew", padx=12, pady=(4, 0))
        notes_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            notes_frame, text="Notes:",
            font=ctk.CTkFont(size=12), text_color=TEXT_MAIN,
        ).grid(row=0, column=0, padx=(0, 8), sticky="w")
        self.entry_notes = ctk.CTkEntry(
            notes_frame,
            placeholder_text="Optional notes for this record",
            text_color=TEXT_MAIN,
        )
        self.entry_notes.grid(row=0, column=1, sticky="ew")

        # ── Bottom action bar ─────────────────────────────────────────────
        bottom = ctk.CTkFrame(self, corner_radius=0, fg_color=BG_BOTTOM)
        bottom.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        self.btn_prev = ctk.CTkButton(
            bottom, text="◀  Previous", width=120,
            command=self._go_previous,
            fg_color=BTN_GRAY, text_color="white",
        )
        self.btn_prev.pack(side="left", padx=12, pady=10)

        self.btn_skip = ctk.CTkButton(
            bottom, text="Skip / N/A", width=110,
            command=self._skip_record,
            fg_color=BTN_ORANGE, text_color="white",
        )
        self.btn_skip.pack(side="left", padx=4, pady=10)

        self.lbl_save_status = ctk.CTkLabel(
            bottom, text="",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_GREEN,
        )
        self.lbl_save_status.pack(side="left", padx=16)

        self.btn_save_next = ctk.CTkButton(
            bottom, text="Save & Next  ▶", width=150,
            command=self._save_and_next,
            fg_color=BTN_BLUE, text_color="white",
        )
        self.btn_save_next.pack(side="right", padx=12, pady=10)

        self.btn_save = ctk.CTkButton(
            bottom, text="Save", width=90,
            command=self._save,
            fg_color=BTN_GREEN, text_color="white",
        )
        self.btn_save.pack(side="right", padx=4, pady=10)

        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._save_and_next())
        self.bind("<Left>",   lambda e: self._go_previous())
        self.bind("<Right>",  lambda e: self._save_and_next())

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
            self.current_index = 0
            self._set_loaded(True)
            self._load_record(self.current_index)
            out_path = self.excel.get_output_path()
            self.lbl_save_path.configure(text=f"Scores saving to: {out_path}")
        except Exception as e:
            messagebox.showerror("Error loading file", str(e))

    def _set_loaded(self, loaded: bool):
        state = "normal" if loaded else "disabled"
        for widget in (self.btn_prev, self.btn_skip, self.btn_save,
                       self.btn_save_next, self.entry_notes, self.cb_filter):
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

        self._update_progress()
        self._update_tab_labels()
        self.lbl_save_status.configure(text="")
        self.btn_prev.configure(state="normal" if index > 0 else "disabled")

    def _go_previous(self):
        if self.current_index > 0:
            self._load_record(self.current_index - 1)

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
                text=f"✓ Saved — {timestamp}", text_color=TEXT_GREEN,
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

    def _skip_record(self):
        answers = self._collect_answers()
        answers["status"] = "skipped"
        try:
            self.excel.write_row(self.current_index, answers)
            self.lbl_save_status.configure(
                text="⟳ Marked as skipped", text_color=TEXT_AMBER,
            )
            self._update_progress()
            self._go_next()
        except Exception as e:
            messagebox.showerror("Save error", str(e))

    # ------------------------------------------------------------------ #
    #  UI Updates                                                          #
    # ------------------------------------------------------------------ #

    def _on_answer_change(self):
        self._update_tab_labels()

    def _update_tab_labels(self):
        q = "Quality ✓" if self.quality_tab.is_complete() else "Quality"
        s = "Structures ✓" if self.structure_tab.is_complete() else "Structures"
        p = "Pathology ✓" if self.pathology_tab.is_complete() else "Pathology"
        self.title(f"MSK Data Collector  |  [{q}]  [{s}]  [{p}]")

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

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        if self._dark_mode:
            ctk.set_appearance_mode("Dark")
            self.btn_theme.configure(text="Light Mode")
        else:
            ctk.set_appearance_mode("Light")
            self.btn_theme.configure(text="Dark Mode")
