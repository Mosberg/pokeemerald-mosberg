# Build script for pokeemerald-expansion on Windows via WSL
# Usage: .\build.ps1 [make arguments]
# Examples:
#   .\build.ps1              # Normal build
#   .\build.ps1 clean        # Clean build artifacts
#   .\build.ps1 -j4          # Build with 4 parallel jobs (default: all cores)

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WSLProjectDir = wsl -d Ubuntu -- wslpath $ProjectDir.Replace('\', '\\')
$WSLGitDir = "/mnt/d/Projects/Pokemon/pokeemerald-expansion/.git/worktrees/pokeemerald-expansion-build-automation"

$Jobs = (wsl -d Ubuntu -- nproc).Trim()
$MakeArgs = if ($args.Count -gt 0) { $args -join ' ' } else { "-j$Jobs" }

Write-Host "Building pokeemerald-expansion with: make $MakeArgs" -ForegroundColor Cyan

wsl -d Ubuntu -- bash -c "export GIT_DIR=$WSLGitDir && cd $WSLProjectDir && make $MakeArgs"

if ($LASTEXITCODE -eq 0) {
    if (Test-Path "$ProjectDir\pokeemerald.gba") {
        $rom = Get-Item "$ProjectDir\pokeemerald.gba"
        Write-Host "`nBuild succeeded! ROM: pokeemerald.gba ($([math]::Round($rom.Length / 1MB, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "`nBuild succeeded!" -ForegroundColor Green
    }
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}
