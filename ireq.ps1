<#
.SYNOPSIS
    Устанавливает зависимости из req.txt, если активирован venv и файл существует.
#>

# Проверяем, активирован ли venv
$isVenvActive = $env:VIRTUAL_ENV -ne $null

if (-not $isVenvActive) {
    Write-Host "Виртуальное окружение Python не активировано." -ForegroundColor Red
    exit 1
}

# Проверяем наличие файла req.txt
$reqFile = "req.txt"
if (-not (Test-Path -Path $reqFile -PathType Leaf)) {
    Write-Host "Файл req.txt не найден в текущей директории." -ForegroundColor Red
    exit 1
}

# Выполняем установку зависимостей
Write-Host "Установка зависимостей из req.txt..." -ForegroundColor Green
pip install -r $reqFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Зависимости успешно установлены." -ForegroundColor Green
} else {
    Write-Host "Ошибка при установке зависимостей." -ForegroundColor Red
    exit $LASTEXITCODE
}