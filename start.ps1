# Run from a PowerShell terminal in this folder: powershell -ExecutionPolicy Bypass -File .\start.ps1
# Uses the installed Python launcher or Python command; no administrator access needed.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) { & py -m venv .venv }
    else { & python -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Could not create environment. Use the full path to your installed Python; see README.md.' }
}
& ./.venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check internet access and retry.' }
& ./.venv/Scripts/python.exe -m streamlit run app.py
