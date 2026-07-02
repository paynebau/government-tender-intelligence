$Python = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Error "Python 3.12 was not found at: $Python"
    Write-Error "Install Python 3.12 first, then run this script again."
    exit 1
}

Set-Location -LiteralPath $PSScriptRoot
& $Python -m pip install -r requirements.txt
& $Python -m streamlit run app.py --server.port 8501 --server.address localhost
