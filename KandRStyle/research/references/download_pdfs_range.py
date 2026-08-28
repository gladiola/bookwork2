#!/usr/bin/env python3
"""
Script to download URL ranges as PDFs using playwright with Firefox support
"""

import openpyxl
import os
import sys
import time
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Get the script directory and construct relative paths
SCRIPT_DIR = Path(__file__).parent.resolve()
WORKBOOK_PATH = SCRIPT_DIR / "Reference_Tracking.xlsx"
PDF_DIR = SCRIPT_DIR

def load_urls_from_workbook(start_id=1, end_id=10):
    """Load URLs from the Reference Tracking workbook within a specified range"""
    wb = openpyxl.load_workbook(str(WORKBOOK_PATH))
    ws = wb["Reference Tracking"]
    
    urls = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:  # ID and URL columns
            url_id = row[0]
            if start_id <= url_id <= end_id:
                urls.append({
                    'id': url_id,
                    'url': row[1],
                    'status': row[2] if len(row) > 2 else "Not Found"
                })
    
    return urls

def update_workbook_status(url_id, status, notes=""):
    """Update the status of a URL in the workbook"""
    wb = openpyxl.load_workbook(str(WORKBOOK_PATH))
    ws = wb["Reference Tracking"]
    
    # Find the row with the matching ID
    for row in ws.iter_rows(min_row=2):
        if row[0].value == url_id:
            row[2].value = status  # Update Status column
            if notes:
                row[3].value = notes  # Update Notes column
            break
    
    wb.save(str(WORKBOOK_PATH))

def download_url_as_pdf(url, pdf_path, browser_type='chromium', timeout=30000):
    """Download a URL as PDF using playwright"""
    try:
        with sync_playwright() as p:
            # Launch the specified browser
            if browser_type == 'firefox':
                browser = p.firefox.launch(headless=True)
            elif browser_type == 'webkit':
                browser = p.webkit.launch(headless=True)
            else:  # default to chromium
                browser = p.chromium.launch(headless=True)
            
            context = browser.new_context()
            page = context.new_page()
            
            print(f"  Navigating to {url}...")
            # Navigate to the URL
            page.goto(url, timeout=timeout, wait_until="networkidle")
            
            # Wait a bit for any JavaScript to execute
            page.wait_for_timeout(2000)
            
            print(f"  Generating PDF...")
            # Generate PDF
            page.pdf(path=pdf_path, format='A4', print_background=True)
            
            browser.close()
            return True, "Successfully downloaded"
            
    except PlaywrightTimeoutError:
        return False, "Timeout - page took too long to load"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    parser = argparse.ArgumentParser(
        description='Download reference URLs as PDFs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Download references 1-10:
    python download_pdfs_range.py --start 1 --end 10
    
  Download references 20-30 using Firefox:
    python download_pdfs_range.py --start 20 --end 30 --browser firefox
    
  Download a single reference (ID 5):
    python download_pdfs_range.py --start 5 --end 5
        """
    )
    
    parser.add_argument('--start', type=int, default=1,
                        help='Starting reference ID (default: 1)')
    parser.add_argument('--end', type=int, default=10,
                        help='Ending reference ID (default: 10)')
    parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'],
                        default='chromium',
                        help='Browser to use for PDF generation (default: chromium)')
    parser.add_argument('--timeout', type=int, default=30000,
                        help='Page load timeout in milliseconds (default: 30000)')
    
    args = parser.parse_args()
    
    print(f"Loading URLs from workbook at: {WORKBOOK_PATH.resolve()}...")
    print(f"Range: {args.start} to {args.end}")
    print(f"Browser: {args.browser}")
    
    urls = load_urls_from_workbook(args.start, args.end)
    
    if not urls:
        print(f"\nNo URLs found in range {args.start}-{args.end}")
        return
    
    print(f"\nFound {len(urls)} URLs to process\n")
    
    results = []
    
    for url_data in urls:
        url_id = url_data['id']
        url = url_data['url']
        pdf_filename = f"ref_{url_id:03d}.pdf"
        pdf_path = PDF_DIR / pdf_filename
        
        print(f"Processing URL {url_id}: {url}")
        
        # Skip local IP addresses
        if "192.168." in url or "127.0.0.1" in url or "localhost" in url:
            print(f"  Skipping local/private URL")
            update_workbook_status(url_id, "Not Found", "Local/private URL - cannot access")
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Skipped',
                'reason': 'Local/private URL'
            })
            continue
        
        # Try to download
        success, message = download_url_as_pdf(url, str(pdf_path), args.browser, args.timeout)
        
        if success:
            print(f"  ✓ Success: {pdf_filename}")
            update_workbook_status(url_id, "Stored", f"Saved as {pdf_filename}")
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Success',
                'filename': pdf_filename
            })
        else:
            print(f"  ✗ Failed: {message}")
            update_workbook_status(url_id, "Not Found", message)
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Failed',
                'reason': message
            })
        
        # Small delay between requests
        time.sleep(2)
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r['status'] == 'Success')
    failed_count = sum(1 for r in results if r['status'] == 'Failed')
    skipped_count = sum(1 for r in results if r['status'] == 'Skipped')
    
    print(f"\nTotal URLs processed: {len(results)}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Skipped: {skipped_count}")
    
    if success_count > 0:
        print("\nSuccessful downloads:")
        for r in results:
            if r['status'] == 'Success':
                print(f"  {r['id']}. {r['filename']} - {r['url'][:60]}...")
    
    if failed_count > 0:
        print("\nFailed downloads:")
        for r in results:
            if r['status'] == 'Failed':
                print(f"  {r['id']}. {r['url'][:60]}... - {r['reason']}")
    
    if skipped_count > 0:
        print("\nSkipped URLs:")
        for r in results:
            if r['status'] == 'Skipped':
                print(f"  {r['id']}. {r['url'][:60]}... - {r['reason']}")

if __name__ == "__main__":
    main()
