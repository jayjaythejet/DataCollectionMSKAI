# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
python3 app.py             # Knee (backward-compat alias)
python3 app_knee.py        # Knee (explicit)
python3 app_shoulder.py    # Shoulder
```

## Installing Dependencies

```bash
pip3 install -r requirements.txt
```

## Building Standalone Executables

```bash
./build_app.sh
# Builds both:
#   dist/MSK_Knee_DataCollector      (.app on Mac, .exe on Windows)
#   dist/MSK_Shoulder_DataCollector  (.app on Mac, .exe on Windows)
```

## Architecture

The project is a CustomTkinter desktop GUI for scoring MRI images. It supports multiple body parts (knee, shoulder) via a shared-code architecture with body-part-specific configs. Each config defines the questions, labels, and encoding for its body part.

**Flow:** `app_knee.py` / `app_shoulder.py` sets the appearance mode globally → creates `MainWindow(config=...)` → user opens an Excel file → `ExcelHandler.load()` reads accessions and auto-adds any missing answer columns → each record is displayed one at a time with the accession copied to clipboard → user scores three tabs → Save writes back to Excel via `ExcelHandler.write_row()`.

### Key files

- `app.py` — backward-compat alias, launches knee app
- `app_knee.py` / `app_shoulder.py` — body-part entry points
- `configs/base.py` — `AppConfig` dataclass, shared encoding helpers
- `configs/knee.py` / `configs/shoulder.py` — body-part configs with items/labels
- `ui/main_window.py` — main window, accepts `config` param
- `ui/quality_tab.py`, `ui/structure_tab.py`, `ui/pathology_tab.py` — scoring tabs, accept items/encoding params
- `data/excel_handler.py` — Excel read/write, accepts `answer_columns` param
- `build_app.sh` — builds both executables via PyInstaller

### Key design decisions

- **`ctk.set_appearance_mode("Light")` and `ctk.set_default_color_theme("blue")` must be called in the entry point file before any CTk widget is imported or created.** Moving these calls anywhere else (e.g. inside `MainWindow.__init__`) causes text to be invisible on macOS.
- All widget colors use explicit hardcoded hex strings — never tuple-style `("light_color", "dark_color")` — to avoid macOS rendering bugs.
- `ExcelHandler` owns all openpyxl logic. It accepts `answer_columns` from the config and auto-creates missing columns in the output file.
- The three tab classes (`QualityTab`, `StructureTab`, `PathologyTab`) are config-driven: each accepts items/encoding params and exposes `get_values()`, `set_values(data)`, `unanswered_fields()`, and `is_complete()`. `MainWindow` passes config to each tab.
- `AppConfig.answer_columns` is a computed property derived from the items lists + `["notes", "status"]` — no need to maintain a separate column list.

### Adding a new body part

1. Create `configs/<bodypart>.py` with an `AppConfig(...)` defining all items.
2. Create `app_<bodypart>.py` following the same pattern as `app_knee.py`.
3. Add a build step in `build_app.sh` and `.github/workflows/build.yml`.

### Adding a new question to an existing body part

1. Add a `(key, label)` tuple to `quality_items` / `structure_items`, or a `(key, label, choices)` tuple to `pathology_items` in the relevant config file (`configs/knee.py` or `configs/shoulder.py`).
2. No other changes needed — `answer_columns` is auto-derived, and tabs use the config items.

### Excel column contract

Each body part writes its own set of columns (auto-derived from config). All share:

**Meta:** `notes`, `status` (values: `complete` / `incomplete` / `skipped`)

**Knee columns:** see `configs/knee.py`
**Shoulder columns:** see `configs/shoulder.py`
