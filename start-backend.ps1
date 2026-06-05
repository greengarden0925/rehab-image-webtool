$env:WEBTOOL_MODE = "1"
Set-Location $PSScriptRoot\backend
& "$PSScriptRoot\..\venv\Scripts\uvicorn.exe" server:app --reload --port 8000
