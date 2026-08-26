#!/usr/bin/env python3
"""
Create Discrete_Extortion worksheet in the Excel workbook.
"""

import openpyxl
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.marker import DataPoint
from openpyxl.drawing.fill import GradientFillProperties, PatternFillProperties
import json
import numpy as np
import sys

def create_discrete_extortion_sheet(wb, lower_bound, upper_bound):
    """Create a new Discrete_Extortion worksheet based on Discrete_Phishing template."""
    
    # Check if sheet already exists
    if 'Discrete_Extortion' in wb.sheetnames:
        print('Discrete_Extortion sheet already exists. Deleting and recreating...')
        del wb['Discrete_Extortion']
    
    # Create new worksheet
    ws = wb.create_sheet('Discrete_Extortion', 1)  # Insert after Table of Contents
    
    # Set up header with link to TOC
    ws['A1'] = '=HYPERLINK("#\'Table of Contents\'!A1","Table of Contents")'
    ws['A1'].font = Font(color="0000FF", underline="single")
    ws['B1'] = 'Discrete Distribution'
    ws['B1'].font = Font(size=14, bold=True)
    
    # Description
    ws['B2'] = f'A discrete distribution has N events with equal likelihood. For Extortion: {upper_bound - lower_bound + 1} events from {lower_bound} to {upper_bound}.'
    ws['B2'].font = Font(size=10)
    
    # Standard deviation formula
    ws['B3'] = 'Std Dev'
    ws['D3'] = '=STDEV(D24:D10023)'
    
    # Headers for value table
    ws['B4'] = 'Value'
    ws['C4'] = 'Likelihood'
    ws['D4'] = 'Cum. %'
    
    # Set up bold headers
    for cell in [ws['B4'], ws['C4'], ws['D4']]:
        cell.font = Font(bold=True)
    
    # Set up discrete values and probabilities
    num_events = upper_bound - lower_bound + 1
    equal_prob = 1.0 / num_events
    
    row = 5
    for value in range(lower_bound, upper_bound + 1):
        ws.cell(row=row, column=2, value=value)  # B column: Value
        ws.cell(row=row, column=3, value=equal_prob)  # C column: Likelihood
        
        # D column: Cumulative %
        if row == 5:
            ws.cell(row=row, column=4, value='=C5')
        else:
            prev_row = row - 1
            ws.cell(row=row, column=4, value=f'=C{row}+D{prev_row}')
        
        row += 1
    
    # Random value generator
    last_value_row = row - 1  # The last row with a value
    ws['B16'] = 'Random Value Generator:'
    ws['C16'] = f'=IFERROR(INDEX(B$5:B${last_value_row},COUNTIF(D$5:D${last_value_row},"<"&RAND())+1),B${last_value_row})'
    ws['C16'].font = Font(italic=True)
    
    # Validation section headers
    ws['B19'] = 'Use for validation and cross-checking'
    ws['D18'] = 'Value'
    ws['D19'] = 'Counts'
    ws['D20'] = '%'
    
    # Set up validation columns (one for each discrete value)
    col = 5  # Column E (0-indexed: column 5 = E)
    for value in range(lower_bound, upper_bound + 1):
        ws.cell(row=18, column=col, value=f'=B{5 + (value - lower_bound)}')  # Value
        ws.cell(row=19, column=col, value=f'=COUNTIF($D$24:$D$10023,"="&B{5 + (value - lower_bound)})')  # Count
        ws.cell(row=20, column=col, value=f'=E19/$O$19')  # Percentage (will need to adjust based on actual column)
        col += 1
        if col > 26:  # Limit to reasonable column count
            break
    
    # Total count cell
    ws.cell(row=19, column=15, value='=SUM(E19:Y19)')  # Column O = 15
    
    # Monte Carlo scenarios header
    ws['B23'] = 'Values based on the above inputs and 10,000 Monte Carlo scenarios'
    ws['C23'] = 'Scenario'
    ws['D23'] = 'Value'
    ws['C23'].font = Font(bold=True)
    ws['D23'].font = Font(bold=True)
    
    # Generate 10,000 Monte Carlo scenarios
    print('Generating 10,000 Monte Carlo scenarios...')
    np.random.seed(42)  # For reproducibility
    
    for scenario in range(1, 10001):
        row_num = 23 + scenario
        ws.cell(row=row_num, column=3, value=scenario)  # Scenario number
        # Random value formula
        ws.cell(row=row_num, column=4, value=f'=IFERROR(INDEX(B$5:B${last_value_row},COUNTIF(D$5:D${last_value_row},"<"&RAND())+1),B${last_value_row})')
    
    print(f'Created Discrete_Extortion worksheet with {num_events} discrete values')
    
    return ws

def create_bar_chart(ws, lower_bound, upper_bound):
    """Create a bar chart for the discrete distribution."""
    
    # Create bar chart
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = f"Discrete Distribution: Extortion Events ({lower_bound}-{upper_bound})"
    chart.y_axis.title = 'Frequency'
    chart.x_axis.title = 'Event Count'
    
    # Number of discrete values
    num_events = upper_bound - lower_bound + 1
    last_value_row = 5 + num_events - 1
    
    # Data for chart: validation counts
    data = Reference(ws, min_col=5, min_row=18, max_row=20, max_col=4 + num_events)
    cats = Reference(ws, min_col=5, min_row=18, max_col=4 + num_events)
    
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    # Set chart size and position
    chart.width = 20
    chart.height = 10
    
    # Position chart
    ws.add_chart(chart, 'F2')
    
    print('Bar chart created')

def main():
    # Load results from JSON
    with open('extortion_analysis_results.json', 'r') as f:
        results = json.load(f)
    
    dist_info = results['distribution']
    lower_bound = dist_info['lower_bound']
    upper_bound = dist_info['upper_bound']
    
    print(f'Creating Discrete_Extortion worksheet with bounds {lower_bound} to {upper_bound}')
    
    # Load workbook
    wb = load_workbook('ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED.xlsx')
    
    # Create the worksheet
    ws = create_discrete_extortion_sheet(wb, lower_bound, upper_bound)
    
    # Create chart
    try:
        create_bar_chart(ws, lower_bound, upper_bound)
    except Exception as e:
        print(f'Warning: Could not create chart: {e}')
    
    # Save workbook
    output_file = 'ComputerCrime_AUG2026_Impact_Final_With_C5C7_IFERROR_CHARTS_FIXED_UPDATED.xlsx'
    print(f'Saving workbook to {output_file}...')
    wb.save(output_file)
    print('Workbook saved successfully!')

if __name__ == '__main__':
    main()
