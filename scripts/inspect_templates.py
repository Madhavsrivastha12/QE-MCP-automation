#!/usr/bin/env python3
"""
Inspect Excel template files to understand structure and formatting
"""

import pandas as pd
import xlrd
from pathlib import Path

def inspect_excel_template(file_path, template_name):
    """Inspect Excel file structure"""
    print(f"\n{'='*80}")
    print(f"INSPECTING: {template_name}")
    print(f"PATH: {file_path}")
    print(f"{'='*80}\n")

    # Open workbook
    workbook = xlrd.open_workbook(file_path, formatting_info=True)

    print(f"Total Sheets: {workbook.nsheets}")
    print(f"Sheet Names: {workbook.sheet_names()}\n")

    # Inspect each sheet
    for sheet_idx in range(workbook.nsheets):
        sheet = workbook.sheet_by_index(sheet_idx)
        sheet_name = sheet.name

        print(f"--- SHEET: {sheet_name} ---")
        print(f"Rows: {sheet.nrows}")
        print(f"Columns: {sheet.ncols}\n")

        # Read headers (assuming row 0)
        if sheet.nrows > 0:
            headers = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell(0, col_idx)
                headers.append(str(cell.value).strip())

            print("COLUMN HEADERS:")
            for idx, header in enumerate(headers, 1):
                print(f"  {idx}. {header}")
            print()

        # Show first few data rows as sample
        if sheet.nrows > 1:
            print("SAMPLE DATA (first 3 rows):")
            for row_idx in range(1, min(4, sheet.nrows)):
                row_data = []
                for col_idx in range(sheet.ncols):
                    cell = sheet.cell(row_idx, col_idx)
                    row_data.append(str(cell.value)[:50])  # Limit cell display
                print(f"  Row {row_idx}: {row_data[:5]}...")  # Show first 5 columns
            print()

        print(f"{'-'*80}\n")

def main():
    # Template paths
    test_scenarios_template = r"C:\Users\TI\Downloads\Forecast API_ Test-Scenarios-Mapped-to-AC 2.xls"
    test_cases_template = r"C:\Users\TI\Downloads\Forecast_API_Consolidated_Test_Cases.xls"

    # Inspect both templates
    if Path(test_scenarios_template).exists():
        inspect_excel_template(test_scenarios_template, "TEST SCENARIOS TEMPLATE")
    else:
        print(f"ERROR: Test Scenarios template not found: {test_scenarios_template}")

    if Path(test_cases_template).exists():
        inspect_excel_template(test_cases_template, "TEST CASES TEMPLATE")
    else:
        print(f"ERROR: Test Cases template not found: {test_cases_template}")

if __name__ == '__main__':
    main()