# PowerShell script to create virtual environment with specific Python version
# Usage: .\create_venv.ps1 [python_version]
# Example: .\create_venv.ps1 3.12

param(
    [string]$PythonVersion = "3.11"
)

Write-Host "Creating virtual environment with Python $PythonVersion..." -ForegroundColor Cyan

# Remove existing .venv if it exists
if (Test-Path .venv) {
    Write-Host "Removing existing .venv directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}

# Try to create venv with specified Python version
try {
    if ($PythonVersion -eq "3.11" -or $PythonVersion -eq "") {
        python -m venv .venv
    } else {
        py -$PythonVersion -m venv .venv
    }
    
    if (Test-Path .venv\Scripts\python.exe) {
        $version = .\.venv\Scripts\python.exe --version
        Write-Host "✓ Virtual environment created successfully!" -ForegroundColor Green
        Write-Host "  Python version: $version" -ForegroundColor Green
        Write-Host ""
        Write-Host "To activate, run:" -ForegroundColor Cyan
        Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Error creating virtual environment: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Trying with default Python..." -ForegroundColor Yellow
    python -m venv .venv
    if (Test-Path .venv\Scripts\python.exe) {
        $version = .\.venv\Scripts\python.exe --version
        Write-Host "✓ Virtual environment created with default Python!" -ForegroundColor Green
        Write-Host "  Python version: $version" -ForegroundColor Green
    }
}

