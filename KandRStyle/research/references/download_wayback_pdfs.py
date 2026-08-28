#!/usr/bin/env python3
"""
Script to download URLs from Internet Archive's Wayback Machine using archived snapshots
Extracts "Accessed" dates from ut.tex and uses them to find appropriate snapshots
"""

import openpyxl
import os
import sys
import time
import argparse
import requests
import re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Get the script directory and construct relative paths
SCRIPT_DIR = Path(__file__).parent.resolve()
UT_TEX_PATH = SCRIPT_DIR / ".." / ".." / "ut.tex"
WORKBOOK_PATH = SCRIPT_DIR / "Reference_Tracking.xlsx"
PDF_DIR = SCRIPT_DIR

# Wayback Machine API endpoint
WAYBACK_API = "http://archive.org/wayback/available"

def extract_accessed_dates_from_tex():
    """
    Extract URLs and their "Accessed" dates from ut.tex
    Returns: dict mapping URLs to accessed dates
    """
    url_dates = {}
    
    with open(str(UT_TEX_PATH), 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Pattern to find endnotes with URLs and Accessed dates
    # Example: \url{https://www.mybib.com}. Accessed 12 July 2026.
    pattern = r'\\url\{([^}]+)\}[^}]*?Accessed\s+(\d+)\s+(\w+)\.?\s+(\d{4})'
    
    matches = re.finditer(pattern, content, re.IGNORECASE)
    
    for match in matches:
        url = match.group(1)
        day = match.group(2)
        month_name = match.group(3)
        year = match.group(4)
        
        # Convert month name to number
        try:
            date_str = f"{day} {month_name} {year}"
            date_obj = datetime.strptime(date_str, "%d %B %Y")
            url_dates[url] = date_obj
        except ValueError:
            try:
                # Try abbreviated month
                date_str = f"{day} {month_name} {year}"
                date_obj = datetime.strptime(date_str, "%d %b %Y")
                url_dates[url] = date_obj
            except ValueError:
                # Skip if date can't be parsed
                pass
    
    return url_dates

def extract_year_from_url(url):
    """
    Extract a year from URL path (e.g., /2015/ or /2020/)
    Returns: year as integer or None if not found
    """
    # Look for 4-digit years in the URL path
    # Pattern matches /YYYY/ or /YYYY- or -YYYY/ or -YYYY-
    year_pattern = r'/(\d{4})(?:/|-|$)|(?:^|/)(\d{4})-'
    matches = re.finditer(year_pattern, url)
    
    for match in matches:
        year_str = match.group(1) or match.group(2)
        year = int(year_str)
        # Only accept reasonable years (1990-2030)
        if 1990 <= year <= 2030:
            return year
    
    return None

def get_wayback_snapshot(url, target_date=None):
    """
    Query Wayback Machine API to find closest snapshot to target_date
    If no target_date provided, gets the latest snapshot
    Returns: (wayback_url, snapshot_timestamp) or (None, None) if not found
    """
    try:
        params = {'url': url}
        if target_date:
            # Format: YYYYMMDD
            params['timestamp'] = target_date.strftime('%Y%m%d')
        
        response = requests.get(WAYBACK_API, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
            snapshot = data['archived_snapshots']['closest']
            if snapshot.get('available'):
                return snapshot['url'], snapshot['timestamp']
        
        return None, None
        
    except Exception as e:
        print(f"    Error querying Wayback Machine: {str(e)[:100]}")
        return None, None

def load_urls_from_workbook(start_id=1, end_id=10):
    """Load URLs from the Reference Tracking workbook within a specified range"""
    wb = openpyxl.load_workbook(str(WORKBOOK_PATH))
    ws = wb["Reference Tracking"]
    
    urls = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:  # ID and URL columns
            url_id = row[0]
            if start_id <= url_id <= end_id:
                # Try to get accessed date from column C (index 2)
                accessed_date_str = row[2] if len(row) > 2 and row[2] else None
                
                # Parse accessed date if present
                accessed_date = None
                if accessed_date_str:
                    try:
                        accessed_date = datetime.strptime(accessed_date_str, "%d %B %Y")
                    except ValueError:
                        try:
                            accessed_date = datetime.strptime(accessed_date_str, "%d %b %Y")
                        except ValueError:
                            pass  # Will fall back to ut.tex extraction
                
                urls.append({
                    'id': url_id,
                    'url': row[1],
                    'accessed_date': accessed_date,
                    'status': row[3] if len(row) > 3 else "Not Found"
                })
    
    return urls

def update_workbook_status(url_id, status, notes=""):
    """Update the status of a URL in the workbook"""
    wb = openpyxl.load_workbook(str(WORKBOOK_PATH))
    ws = wb["Reference Tracking"]
    
    # Find the row with the matching ID
    for row in ws.iter_rows(min_row=2):
        if row[0].value == url_id:
            row[3].value = status  # Update Status column (now column D)
            if notes:
                row[4].value = notes  # Update Notes column (now column E)
            break
    
    wb.save(str(WORKBOOK_PATH))

def download_wayback_url_as_pdf(wayback_url, pdf_path, browser_type='chromium', timeout=30000):
    """Download a Wayback Machine URL as PDF using playwright"""
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
            
            print(f"    Navigating to Wayback snapshot...")
            # Navigate to the URL
            page.goto(wayback_url, timeout=timeout, wait_until="networkidle")
            
            # Wait a bit for any JavaScript to execute
            page.wait_for_timeout(2000)
            
            print(f"    Generating PDF...")
            # Generate PDF
            page.pdf(path=pdf_path, format='A4', print_background=True)
            
            browser.close()
            return True, "Successfully downloaded from Wayback Machine"
            
    except PlaywrightTimeoutError:
        return False, "Timeout - page took too long to load"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def main():
    parser = argparse.ArgumentParser(
        description='Download reference URLs as PDFs from Internet Archive Wayback Machine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Download references 1-10 from Wayback Machine:
    python download_wayback_pdfs.py --start 1 --end 10
    
  Download references 20-30 using Chromium (explicit):
    python download_wayback_pdfs.py --start 20 --end 30 --browser chromium
    
  Download using specific date (format: YYYY-MM-DD):
    python download_wayback_pdfs.py --start 1 --end 5 --date 2026-07-12

Note: The script uses the following priority for determining the snapshot date:
      1. Explicit --date argument (if provided)
      2. Accessed date from Reference_Tracking.xlsx workbook
      3. Accessed date from ut.tex file
      4. Year extracted from URL (e.g., /2015/ uses July 1, 2015)
      5. Latest available snapshot (if no date information found)
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
    parser.add_argument('--date', type=str,
                        help='Specific date to search for snapshots (YYYY-MM-DD)')
    parser.add_argument('--force-latest', action='store_true',
                        help='(Deprecated: now default behavior) Use latest snapshot if accessed date not found')
    
    args = parser.parse_args()
    
    print(f"Loading URLs from workbook at: {WORKBOOK_PATH.resolve()}...")
    print(f"Range: {args.start} to {args.end}")
    print(f"Browser: {args.browser}")
    
    # Load URLs from workbook (includes accessed dates from column C)
    urls = load_urls_from_workbook(args.start, args.end)
    
    if not urls:
        print(f"\nNo URLs found in range {args.start}-{args.end}")
        return
    
    print(f"\nFound {len(urls)} URLs to process")
    
    # Check how many have accessed dates from workbook
    urls_with_dates = sum(1 for u in urls if u.get('accessed_date'))
    print(f"{urls_with_dates} URLs have 'Accessed' dates in workbook")
    
    # Extract accessed dates from ut.tex as fallback
    print(f"\nExtracting additional 'Accessed' dates from ut.tex as fallback...")
    url_dates = extract_accessed_dates_from_tex()
    print(f"Found {len(url_dates)} URLs with accessed dates in ut.tex\n")
    
    # Use specific date if provided
    specific_date = None
    if args.date:
        try:
            specific_date = datetime.strptime(args.date, "%Y-%m-%d")
            print(f"Using specific date: {specific_date.strftime('%B %d, %Y')}\n")
        except ValueError:
            print(f"Warning: Invalid date format '{args.date}'. Use YYYY-MM-DD\n")
    
    results = []
    
    for url_data in urls:
        url_id = url_data['id']
        url = url_data['url']
        pdf_filename = f"ref_{url_id:03d}_wayback.pdf"
        pdf_path = PDF_DIR / pdf_filename
        
        print(f"Processing URL {url_id}: {url}")
        
        # Skip local IP addresses
        if "192.168." in url or "127.0.0.1" in url or "localhost" in url:
            print(f"  Skipping local/private URL")
            update_workbook_status(url_id, "Not Found", "Local/private URL - cannot archive")
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Skipped',
                'reason': 'Local/private URL'
            })
            continue
        
        # Determine which date to use
        target_date = specific_date
        if not target_date and url_data.get('accessed_date'):
            # Use date from workbook
            target_date = url_data['accessed_date']
            print(f"  Using accessed date from workbook: {target_date.strftime('%B %d, %Y')}")
        elif not target_date and url in url_dates:
            # Fall back to date from ut.tex
            target_date = url_dates[url]
            print(f"  Using accessed date from ut.tex: {target_date.strftime('%B %d, %Y')}")
        elif not target_date:
            # Try to extract year from URL
            year = extract_year_from_url(url)
            if year:
                # Use July 1st of that year as the target date
                target_date = datetime(year, 7, 1)
                print(f"  Extracted year {year} from URL - using {target_date.strftime('%B %d, %Y')}")
            else:
                print(f"  No accessed date found - using latest available snapshot")
        
        # Query Wayback Machine
        print(f"  Querying Wayback Machine...")
        wayback_url, snapshot_timestamp = get_wayback_snapshot(url, target_date)
        
        if not wayback_url:
            print(f"  ✗ No archived snapshot found")
            update_workbook_status(url_id, "Not Found", "No Wayback Machine snapshot available")
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Failed',
                'reason': 'No Wayback snapshot'
            })
            continue
        
        # Parse snapshot timestamp
        snapshot_date = datetime.strptime(snapshot_timestamp, "%Y%m%d%H%M%S")
        print(f"  Found snapshot from: {snapshot_date.strftime('%B %d, %Y')}")
        
        # Try to download
        success, message = download_wayback_url_as_pdf(wayback_url, str(pdf_path), args.browser, args.timeout)
        
        if success:
            print(f"  ✓ Success: {pdf_filename}")
            note = f"Saved as {pdf_filename} (Wayback: {snapshot_date.strftime('%Y-%m-%d')})"
            update_workbook_status(url_id, "Stored", note)
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Success',
                'filename': pdf_filename,
                'snapshot_date': snapshot_date
            })
        else:
            print(f"  ✗ Failed: {message}")
            update_workbook_status(url_id, "Not Found", f"Wayback download failed: {message}")
            results.append({
                'id': url_id,
                'url': url,
                'status': 'Failed',
                'reason': message
            })
        
        # Small delay between requests to be nice to Archive.org
        time.sleep(3)
    
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
                snapshot_str = r['snapshot_date'].strftime('%Y-%m-%d')
                print(f"  {r['id']}. {r['filename']} (snapshot: {snapshot_str})")
    
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
