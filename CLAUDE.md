# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
python3 app.py
```

## Installing Dependencies

```bash
pip3 install -r requirements.txt
```

## Building a Standalone Executable

```bash
./build_app.sh
# Mac output: dist/MSK_DataCollector.app
# Windows output: dist/MSK_DataCollector.exe  (must be run on Windows)
```

## Architecture

The app is a CustomTkinter desktop GUI for scoring MRI knee images. It reads an Excel file with pre-populated accession numbers and writes scoring answers back to that same file in-place.

**Flow:** `app.py` sets the appearance mode globally → creates `MainWindow` → user opens an Excel file → `ExcelHandler.load()` reads accessions and auto-adds any missing answer columns → each record is displayed one at a time with the accession copied to clipboard → user scores three tabs → Save writes back to Excel via `ExcelHandler.write_row()`.

### Key design decisions

- **`ctk.set_appearance_mode("Light")` and `ctk.set_default_color_theme("blue")` must be called in `app.py` before any CTk widget is imported or created.** Moving these calls anywhere else (e.g. inside `MainWindow.__init__`) causes text to be invisible on macOS.
- All widget colors use explicit hardcoded hex strings — never tuple-style `("light_color", "dark_color")` — to avoid macOS rendering bugs.
- `ExcelHandler` owns all openpyxl logic. It maps column names to column indices on load and auto-creates missing answer columns in the header row. All other columns in the user's file are untouched.
- The three tab classes (`QualityTab`, `StructureTab`, `PathologyTab`) are self-contained: each exposes `get_values()`, `set_values(data)`, `unanswered_fields()`, and `is_complete()`. `MainWindow` calls these uniformly without knowing their internal structure.

### Excel column contract

The app reads the `accession` column (case-insensitive header match) and writes these columns (created automatically if absent):

**Quality (Likert 1–5):** `contrast_resolution`, `edge_sharpness`, `fat_suppression`, `fluid_brightness`, `image_noise`, `motion_artifact`, `partial_volume_effects`, `overall_image_quality`

**Structures (Likert 1–5):** `acl_visibility`, `pcl_visibility`, `mcl_visibility`, `lcl_visibility`, `medial_meniscus_visibility`, `lateral_meniscus_visibility`, `extensor_tendons_visibility`, `articular_cartilage_visibility`, `bones_visibility`

**Pathology (Yes/No or None/Partial Thickness/Full Thickness):** `acl_tear`, `pcl_tear`, `mcl_tear`, `lcl_tear`, `medial_meniscus_tear`, `lateral_meniscus_tear`, `articular_cartilage_defect`, `bone_marrow_edema`

**Meta:** `notes`, `status` (values: `complete` / `incomplete` / `skipped`)

### Adding a new question

1. Add a `(key, label)` tuple to `QUALITY_ITEMS` / `STRUCTURE_ITEMS`, or a `(key, label, choices)` tuple to `PATHOLOGY_ITEMS` in the relevant tab file.
2. Add the column name (`key`) to `ANSWER_COLUMNS` in `data/excel_handler.py`.
3. No changes needed in `MainWindow` — it calls `get_values()` / `set_values()` generically.
