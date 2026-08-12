# Launch the pokeemerald-expansion GUI editor
# Usage: .\editor.ps1
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\editor\editor.py"
