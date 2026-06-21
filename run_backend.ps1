# FRC Dashboard Backend Start Script
Write-Host "Starting FRC Dashboard Backend..."
Write-Host ""

# Navigate to backend directory
Set-Location "$PSScriptRoot\frc_dashboard\backend"

# Run the backend server
python src\main.py --port 8000

# Keep window open after script ends
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")