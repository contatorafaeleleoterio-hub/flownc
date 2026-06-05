# Build do EXE portatil (PyInstaller onedir) — PRD secao 6 / Fase 9.
# Gera dist\FlowNC\ com o .exe + _internal + data\presets (editavel).
# Copie a pasta dist\FlowNC inteira para o pen drive e rode o .exe.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = "$root\.venv\Scripts\python.exe"

# Usar `python -m PyInstaller` (o wrapper pyinstaller.exe pode estar quebrado
# apos o venv ser movido de pasta — shebang com caminho absoluto antigo).
Write-Host "Empacotando (onedir, windowed)..." -ForegroundColor Cyan
& $py -m PyInstaller --noconfirm --onedir --windowed --name FlowNC --paths "$root" "$root\main.py"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller falhou (exit $LASTEXITCODE)." }

# Presets ficam AO LADO do exe para o operador editar/adicionar no pen drive.
$dist = "$root\dist\FlowNC"
Copy-Item -Recurse -Force "$root\data" "$dist\data"
Copy-Item -Force "$root\PORTATIL_LEIA-ME.txt" "$dist\LEIA-ME.txt" -ErrorAction SilentlyContinue

Write-Host "OK -> $dist" -ForegroundColor Green
Write-Host "Copie a pasta FlowNC para o pen drive e rode FlowNC.exe"
