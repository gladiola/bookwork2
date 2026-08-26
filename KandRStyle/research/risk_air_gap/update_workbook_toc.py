#!/usr/bin/env python3
"""
Update Table of Contents and add hyperlinks in the workbook.
"""

import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font
import sys

def update_table_of_contents(wb):
    """Update the Table of Contents sheet."""
    
    if 'Table of Contents' not in wb.sheetnames:
        print('Error: Table of Contents sheet not found')
        return False
    
    toc_ws = wb['Table of Contents']
    
    # Find the last row with content
    last_row = 1
    for row in range(1, 100):
        if toc_ws.cell(row=row, column=1).value:
            last_row = row
    
    # Check if Discrete_Extortion is already in TOC
    found = False
    for row in range(1, last_row + 1):
        cell_value = toc_ws.cell(row=row, column=1).value
        if cell_value and 'Discrete_Extortion' in str(cell_value):
            found = True
            print(f'Discrete_Extortion already in TOC at row {row}')
            break
    
    if not found:
        # Add Discrete_Extortion to TOC
        # Find where to insert it (after other Discrete sheets)
        insert_row = last_row + 1
        for row in range(1, last_row + 1):
            cell_value = toc_ws.cell(row=row, column=1).value
            if cell_value and 'Discrete' in str(cell_value):
                insert_row = row + 1
        
        # Create hyperlink
        toc_ws.cell(row=insert_row, column=1).value = 'Discrete_Extortion'
        toc_ws.cell(row=insert_row, column=1).hyperlink = '#Discrete_Extortion!A1'
        toc_ws.cell(row=insert_row, column=1).font = Font(color="0000FF", underline="single")
        
        print(f'Added Discrete_Extortion to TOC at row {insert_row}')
    
    return True

def add_toc_hyperlinks(wb):
    """Add hyperlinks back to TOC from all worksheets."""
    
    toc_link = '=HYPERLINK("#\'Table of Contents\'!A1","Table of Contents")'
    toc_font = Font(color="0000FF", underline="single")
    
    # Iterate through all sheets
    for sheet_name in wb.sheetnames:
        if sheet_name == 'Table of Contents':
            continue
            
        ws = wb[sheet_name]
        
        # Check if A1 already has a TOC link
        cell_value = ws['A1'].value
        if cell_value and 'Table of Contents' in str(cell_value):
            # Already has link
            continue
        
        # Add TOC link to A1
        ws['A1'] = toc_link
        ws['A1'].font = toc_font
        
        print(f'Added TOC link to {sheet_name}')
    
    return True

def validate_charts(wb):
    """Check if charts exist and are properly configured."""
    
    chart_sheets = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        if hasattr(ws, '_charts') and len(ws._charts) > 0:
            chart_sheets.append((sheet_name, len(ws._charts)))
    
    print(f'\nWorksheets with charts:')
    for sheet_name, num_charts in chart_sheets:
        print(f'  {sheet_name}: {num_charts} chart(s)')
    
    return True

def main():
    input_file = 'ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED_UPDATED.xlsx'
    output_file = 'ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx'
    
    print(f'Loading workbook: {input_file}')
    wb = load_workbook(input_file)
    
    print(f'\nTotal worksheets: {len(wb.sheetnames)}')
    
    # Update Table of Contents
    print('\n=== Updating Table of Contents ===')
    update_table_of_contents(wb)
    
    # Add TOC hyperlinks
    print('\n=== Adding TOC hyperlinks to all worksheets ===')
    add_toc_hyperlinks(wb)
    
    # Validate charts
    print('\n=== Validating charts ===')
    validate_charts(wb)
    
    # Save the workbook
    print(f'\n=== Saving workbook to {output_file} ===')
    wb.save(output_file)
    print('Workbook saved successfully!')
    
    # Verify the file
    print('\n=== Verifying saved workbook ===')
    wb_verify = load_workbook(output_file)
    print(f'Worksheets in saved file: {len(wb_verify.sheetnames)}')
    
    # Check if Discrete_Extortion exists
    if 'Discrete_Extortion' in wb_verify.sheetnames:
        print('✓ Discrete_Extortion worksheet exists')
        ws = wb_verify['Discrete_Extortion']
        print(f'  - Max row: {ws.max_row}')
        print(f'  - Max column: {ws.max_column}')
        print(f'  - TOC link: {ws["A1"].value}')
    else:
        print('✗ Discrete_Extortion worksheet NOT found')
    
    print('\nUpdate complete!')

if __name__ == '__main__':
    main()
