"""
Excel read/write handler using openpyxl.
Reads accession numbers and reads/writes answer columns in-place.
"""
import openpyxl
from datetime import datetime

# All columns the app writes (in addition to reading 'accession')
ANSWER_COLUMNS = [
    # Section 1: Image Quality (Likert 1-5)
    "contrast_resolution", "edge_sharpness", "fat_suppression",
    "fluid_brightness", "image_noise", "motion_artifact",
    "partial_volume_effects", "overall_image_quality",
    # Section 2: Structure Visibility (Likert 1-5)
    "acl_visibility", "pcl_visibility", "mcl_visibility", "lcl_visibility",
    "medial_meniscus_visibility", "lateral_meniscus_visibility",
    "extensor_tendons_visibility", "articular_cartilage_visibility",
    "bones_visibility",
    # Section 3: Pathology (Yes/No or No/Partial/Full)
    "acl_tear", "pcl_tear", "mcl_tear", "lcl_tear",
    "medial_meniscus_tear", "lateral_meniscus_tear",
    "articular_cartilage_defect", "bone_marrow_edema",
    # Extras
    "notes", "status",
]


class ExcelHandler:
    def __init__(self):
        self.filepath = None
        self.workbook = None
        self.sheet = None
        self.col_index = {}   # column_name -> col_number (1-based)
        self.accession_col = None
        self.data_rows = []   # list of row numbers (1-based) that have accessions

    def load(self, filepath: str) -> list[str]:
        """
        Load the workbook. Returns list of accession values in order.
        Raises ValueError if no 'accession' column found.
        """
        self.filepath = filepath
        self.workbook = openpyxl.load_workbook(filepath)
        self.sheet = self.workbook.active

        # Map existing header names -> column index
        headers = {}
        for cell in self.sheet[1]:
            if cell.value is not None:
                headers[str(cell.value).strip().lower()] = cell.column

        if "accession" not in headers:
            raise ValueError(
                "No 'accession' column found in the Excel file. "
                "Please ensure the header row has a column named 'accession'."
            )

        self.accession_col = headers["accession"]
        self.col_index = {k: v for k, v in headers.items()}

        # Ensure all answer columns exist as headers
        self._ensure_answer_columns()

        # Collect row numbers that have an accession value
        self.data_rows = []
        for row in range(2, self.sheet.max_row + 1):
            val = self.sheet.cell(row=row, column=self.accession_col).value
            if val is not None and str(val).strip() != "":
                self.data_rows.append(row)

        if not self.data_rows:
            raise ValueError("The Excel file has no accession data rows.")

        return [
            str(self.sheet.cell(row=r, column=self.accession_col).value).strip()
            for r in self.data_rows
        ]

    def _ensure_answer_columns(self):
        """Add any missing answer columns to the header row."""
        # Find next available column
        next_col = self.sheet.max_column + 1

        for col_name in ANSWER_COLUMNS:
            if col_name not in self.col_index:
                self.sheet.cell(row=1, column=next_col, value=col_name)
                self.col_index[col_name] = next_col
                next_col += 1

        self.workbook.save(self.filepath)

    def read_row(self, row_index: int) -> dict:
        """
        Read all answer column values for a given row_index (0-based into data_rows).
        Returns dict of {column_name: value}.
        """
        row = self.data_rows[row_index]
        result = {}
        for col_name in ANSWER_COLUMNS:
            col_num = self.col_index.get(col_name)
            if col_num:
                result[col_name] = self.sheet.cell(row=row, column=col_num).value
            else:
                result[col_name] = None
        return result

    def write_row(self, row_index: int, answers: dict):
        """
        Write answers dict to the Excel row. Saves the file.
        answers: {column_name: value}
        """
        row = self.data_rows[row_index]
        for col_name, value in answers.items():
            col_num = self.col_index.get(col_name)
            if col_num:
                self.sheet.cell(row=row, column=col_num, value=value)
        self.workbook.save(self.filepath)

    def get_completion_status(self) -> dict:
        """
        Returns dict of {row_index: status_string} for all rows.
        Status is read from the 'status' column.
        """
        status_col = self.col_index.get("status")
        result = {}
        for i, row in enumerate(self.data_rows):
            if status_col:
                val = self.sheet.cell(row=row, column=status_col).value
                result[i] = val or "incomplete"
            else:
                result[i] = "incomplete"
        return result

    def get_accession(self, row_index: int) -> str:
        row = self.data_rows[row_index]
        return str(self.sheet.cell(row=row, column=self.accession_col).value).strip()

    def total_records(self) -> int:
        return len(self.data_rows)
