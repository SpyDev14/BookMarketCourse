<#
.SYNOPSIS
    ������������� ����������� �� req.txt, ���� ����������� venv � ���� ����������.
#>

# ���������, ����������� �� venv
$isVenvActive = $env:VIRTUAL_ENV -ne $null

if (-not $isVenvActive) {
    Write-Host "����������� ��������� Python �� ������������." -ForegroundColor Red
    exit 1
}

# ��������� ������� ����� req.txt
$reqFile = "req.txt"
if (-not (Test-Path -Path $reqFile -PathType Leaf)) {
    Write-Host "���� req.txt �� ������ � ������� ����������." -ForegroundColor Red
    exit 1
}

# ��������� ��������� ������������
Write-Host "��������� ������������ �� req.txt..." -ForegroundColor Green
pip install -r $reqFile

if ($LASTEXITCODE -eq 0) {
    Write-Host "����������� ������� �����������." -ForegroundColor Green
} else {
    Write-Host "������ ��� ��������� ������������." -ForegroundColor Red
    exit $LASTEXITCODE
}