$venvScriptPath = ".\.venv\Scripts\Activate.ps1"

if (Test-Path $venvScriptPath) {
    & $venvScriptPath
} else {
    Write-Host "Ошибка: Не найден файл активации виртуального окружения" -ForegroundColor Red
    Write-Host "Убедитесь, что виртуальное окружение создано в папке .venv" -ForegroundColor Yellow
    Write-Host "Можно создать его командой: python -m venv .venv" -ForegroundColor Yellow
}