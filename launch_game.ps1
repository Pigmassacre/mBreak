# mBreak Game Launcher (PowerShell)
# This script launches the mBreak game from the python/ directory

# Get the directory containing this script
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$gamePath = Join-Path -Path $scriptPath -ChildPath "python\mBreak.py"
$pythonDir = Join-Path -Path $scriptPath -ChildPath "python"

# Change to the python directory before launching
Set-Location -Path $pythonDir

# Launch the game
python $gamePath

Write-Host "Game has exited." 