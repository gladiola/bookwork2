# Download-References-Wayback.ps1
# PowerShell script to download reference URLs from Internet Archive Wayback Machine
# Uses archived snapshots based on "Accessed" dates from ut.tex

<#
.SYNOPSIS
    Downloads reference URLs as PDFs from Internet Archive Wayback Machine
.DESCRIPTION
    This script downloads archived versions of reference URLs from the Wayback Machine.
    It automatically uses "Accessed" dates from ut.tex to find appropriate snapshots.
    PDFs are saved with "_wayback" suffix to distinguish from live downloads.
.PARAMETER StartRef
    Starting reference ID (default: 1)
.PARAMETER EndRef
    Ending reference ID (default: 10)
.PARAMETER Browser
    Browser to use: chromium, firefox, or webkit (default: firefox)
.PARAMETER Date
    Specific date to search for snapshots (format: YYYY-MM-DD)
    Overrides "Accessed" dates from ut.tex
.PARAMETER ForceLatest
    Use latest available snapshot even if no "Accessed" date found
.PARAMETER SkipSetup
    Skip checking and installing dependencies
.EXAMPLE
    .\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10
    Downloads references 1-10 using accessed dates from ut.tex
.EXAMPLE
    .\Download-References-Wayback.ps1 -StartRef 1 -EndRef 10 -ForceLatest
    Downloads references 1-10, using latest snapshot if no accessed date
.EXAMPLE
    .\Download-References-Wayback.ps1 -StartRef 20 -EndRef 25 -Date "2026-07-12"
    Downloads references 20-25 using snapshot from July 12, 2026
.EXAMPLE
    .\Download-References-Wayback.ps1 -StartRef 1 -EndRef 157 -Browser firefox
    Downloads ALL references using Firefox
#>

param(
    [Parameter(Mandatory=$false)]
    [int]$StartRef = 1,
    
    [Parameter(Mandatory=$false)]
    [int]$EndRef = 10,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('chromium', 'firefox', 'webkit')]
    [string]$Browser = 'firefox',
    
    [Parameter(Mandatory=$false)]
    [string]$Date = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$ForceLatest,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipSetup
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Wayback Machine PDF Downloader" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-CommandExists {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction SilentlyContinue) {
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

# Function to check Python installation
function Test-Python {
    Write-Host "Checking Python installation..." -ForegroundColor Yellow
    
    if (Test-CommandExists "python") {
        $pythonVersion = python --version 2>&1
        Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
        return $true
    } elseif (Test-CommandExists "python3") {
        $pythonVersion = python3 --version 2>&1
        Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ✗ Python not found!" -ForegroundColor Red
        Write-Host "  Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host "  Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
        return $false
    }
}

# Function to check and install Python packages
function Install-PythonPackages {
    Write-Host "`nChecking Python packages..." -ForegroundColor Yellow
    
    # Check openpyxl
    Write-Host "  Checking openpyxl..." -ForegroundColor Gray
    $openpyxlCheck = python -c "import openpyxl" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Installing openpyxl..." -ForegroundColor Yellow
        python -m pip install openpyxl
    } else {
        Write-Host "    ✓ openpyxl installed" -ForegroundColor Green
    }
    
    # Check requests
    Write-Host "  Checking requests..." -ForegroundColor Gray
    $requestsCheck = python -c "import requests" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Installing requests..." -ForegroundColor Yellow
        python -m pip install requests
    } else {
        Write-Host "    ✓ requests installed" -ForegroundColor Green
    }
    
    # Check playwright
    Write-Host "  Checking playwright..." -ForegroundColor Gray
    $playwrightCheck = python -c "import playwright" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Installing playwright..." -ForegroundColor Yellow
        python -m pip install playwright
        Write-Host "    Installing browser binaries (this may take a few minutes)..." -ForegroundColor Yellow
        python -m playwright install $Browser
        python -m playwright install-deps
    } else {
        Write-Host "    ✓ playwright installed" -ForegroundColor Green
        # Check if browser is installed
        Write-Host "    Checking $Browser browser..." -ForegroundColor Gray
        try {
            python -m playwright install $Browser 2>&1 | Out-Null
            Write-Host "    ✓ $Browser browser installed" -ForegroundColor Green
        } catch {
            Write-Host "    Installing $Browser browser..." -ForegroundColor Yellow
            python -m playwright install $Browser
        }
    }
}

# Function to validate reference range
function Test-ReferenceRange {
    param($Start, $End)
    
    if ($Start -lt 1) {
        Write-Host "Error: Start reference must be at least 1" -ForegroundColor Red
        return $false
    }
    
    if ($End -lt $Start) {
        Write-Host "Error: End reference must be greater than or equal to start reference" -ForegroundColor Red
        return $false
    }
    
    if ($End -gt 157) {
        Write-Host "Warning: Only 157 references exist. Setting end to 157." -ForegroundColor Yellow
        $script:EndRef = 157
    }
    
    return $true
}

# Function to validate date format
function Test-DateFormat {
    param($DateString)
    
    if ([string]::IsNullOrEmpty($DateString)) {
        return $true
    }
    
    try {
        $null = [DateTime]::ParseExact($DateString, "yyyy-MM-dd", $null)
        return $true
    } catch {
        Write-Host "Error: Invalid date format '$DateString'. Use YYYY-MM-DD (e.g., 2026-07-12)" -ForegroundColor Red
        return $false
    }
}

# Main execution
try {
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host "  Start Reference: $StartRef" -ForegroundColor White
    Write-Host "  End Reference:   $EndRef" -ForegroundColor White
    Write-Host "  Browser:         $Browser" -ForegroundColor White
    if ($Date) {
        Write-Host "  Target Date:     $Date" -ForegroundColor White
    } else {
        Write-Host "  Date Source:     Accessed dates from ut.tex" -ForegroundColor White
    }
    if ($ForceLatest) {
        Write-Host "  Force Latest:    Yes (use latest snapshot if no accessed date)" -ForegroundColor White
    }
    Write-Host "  Working Dir:     $ScriptDir" -ForegroundColor White
    Write-Host ""
    
    # Validate range
    if (-not (Test-ReferenceRange -Start $StartRef -End $EndRef)) {
        exit 1
    }
    
    # Validate date if provided
    if (-not (Test-DateFormat -DateString $Date)) {
        exit 1
    }
    
    # Setup checks (unless skipped)
    if (-not $SkipSetup) {
        if (-not (Test-Python)) {
            exit 1
        }
        
        Install-PythonPackages
        Write-Host ""
    }
    
    # Check if the Python script exists
    $pythonScript = Join-Path $ScriptDir "download_wayback_pdfs.py"
    if (-not (Test-Path $pythonScript)) {
        Write-Host "Error: download_wayback_pdfs.py not found in $ScriptDir" -ForegroundColor Red
        exit 1
    }
    
    # Check if workbook exists
    $workbook = Join-Path $ScriptDir "Reference_Tracking.xlsx"
    if (-not (Test-Path $workbook)) {
        Write-Host "Error: Reference_Tracking.xlsx not found in $ScriptDir" -ForegroundColor Red
        Write-Host "Run create_reference_tracker.py first to generate the workbook" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if ut.tex exists
    $utTexPath = Join-Path $ScriptDir "..\..\ut.tex"
    if (-not (Test-Path $utTexPath)) {
        Write-Host "Error: ut.tex not found at $utTexPath" -ForegroundColor Red
        Write-Host "The script needs ut.tex to extract 'Accessed' dates" -ForegroundColor Yellow
        exit 1
    }
    
    # Build command line arguments
    $pythonArgs = @("--start", $StartRef, "--end", $EndRef, "--browser", $Browser)
    if ($Date) {
        $pythonArgs += @("--date", $Date)
    }
    if ($ForceLatest) {
        $pythonArgs += "--force-latest"
    }
    
    # Run the download script
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Starting Wayback Machine download..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $startTime = Get-Date
    
    & python $pythonScript @pythonArgs
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Process completed in $($duration.ToString('mm\:ss'))" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "PDFs are saved in: $ScriptDir" -ForegroundColor Yellow
    Write-Host "  (Files named: ref_XXX_wayback.pdf)" -ForegroundColor Gray
    Write-Host "Workbook updated: $workbook" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Note: PDFs from Wayback Machine include the archived date in the Notes column" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error occurred!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}
