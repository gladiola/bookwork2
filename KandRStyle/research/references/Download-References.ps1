# Download-References.ps1
# PowerShell script to automate downloading reference URLs as PDFs on Windows
# Uses Firefox browser via Playwright

<#
.SYNOPSIS
    Downloads reference URLs as PDFs with range support
.DESCRIPTION
    This script automates the process of downloading reference URLs from the
    Reference Tracking workbook as PDF files using Firefox browser.
.PARAMETER StartRef
    Starting reference ID (default: 1)
.PARAMETER EndRef
    Ending reference ID (default: 10)
.PARAMETER Browser
    Browser to use: chromium, firefox, or webkit (default: firefox)
.PARAMETER SkipSetup
    Skip checking and installing dependencies
.EXAMPLE
    .\Download-References.ps1 -StartRef 1 -EndRef 10
    Downloads references 1 through 10
.EXAMPLE
    .\Download-References.ps1 -StartRef 11 -EndRef 20 -Browser firefox
    Downloads references 11 through 20 using Firefox
.EXAMPLE
    .\Download-References.ps1 -StartRef 1 -EndRef 157
    Downloads all 157 references
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
    [switch]$SkipSetup
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Reference URL PDF Downloader" -ForegroundColor Cyan
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
        Write-Host "  [OK] Found: $pythonVersion" -ForegroundColor Green
        return $true
    } elseif (Test-CommandExists "python3") {
        $pythonVersion = python3 --version 2>&1
        Write-Host "  [OK] Found: $pythonVersion" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  [X] Python not found!" -ForegroundColor Red
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
        Write-Host "    [OK] openpyxl installed" -ForegroundColor Green
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
        Write-Host "    [OK] playwright installed" -ForegroundColor Green
        # Check if browser is installed
        Write-Host "    Checking $Browser browser..." -ForegroundColor Gray
        try {
            python -m playwright install $Browser 2>&1 | Out-Null
            Write-Host "    [OK] $Browser browser installed" -ForegroundColor Green
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

# Main execution
try {
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host "  Start Reference: $StartRef" -ForegroundColor White
    Write-Host "  End Reference:   $EndRef" -ForegroundColor White
    Write-Host "  Browser:         $Browser" -ForegroundColor White
    Write-Host "  Working Dir:     $ScriptDir" -ForegroundColor White
    Write-Host ""
    
    # Validate range
    if (-not (Test-ReferenceRange -Start $StartRef -End $EndRef)) {
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
    $pythonScript = Join-Path $ScriptDir "download_pdfs_range.py"
    if (-not (Test-Path $pythonScript)) {
        Write-Host "Error: download_pdfs_range.py not found in $ScriptDir" -ForegroundColor Red
        exit 1
    }
    
    # Check if workbook exists
    $workbook = Join-Path $ScriptDir "Reference_Tracking.xlsx"
    if (-not (Test-Path $workbook)) {
        Write-Host "Error: Reference_Tracking.xlsx not found in $ScriptDir" -ForegroundColor Red
        Write-Host "Run create_reference_tracker.py first to generate the workbook" -ForegroundColor Yellow
        exit 1
    }
    
    # Run the download script
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Starting download process..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    $startTime = Get-Date
    
    python $pythonScript --start $StartRef --end $EndRef --browser $Browser
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Process completed in $($duration.ToString('mm\:ss'))" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "PDFs are saved in: $ScriptDir" -ForegroundColor Yellow
    Write-Host "Workbook updated: $workbook" -ForegroundColor Yellow
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error occurred!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    exit 1
}
