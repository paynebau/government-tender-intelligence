$Python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Error "Python 3.12 was not found at: $Python"
    exit 1
}

Set-Location -LiteralPath $PSScriptRoot\..
& $Python .\scripts\import_to_sqlite.py @args
