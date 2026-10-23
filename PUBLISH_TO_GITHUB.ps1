# Run from the extracted project folder. This never modifies a different local folder.
$ErrorActionPreference = 'Stop'
$remote = 'https://github.com/AryanGaur2504/ProofGraph.git'
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git must be installed.' }
if (-not (Test-Path 'frontend/package.json')) { throw 'Run this inside the extracted ProofGraph project folder.' }
if (-not (Test-Path '.git')) { git init }
$found = git remote | Select-String '^origin$'
if (-not $found) { git remote add origin $remote }
$origin = git remote get-url origin
if ($origin -ne $remote) { throw "Unexpected remote: $origin. Refusing to change a different repository." }
git fetch origin
if ($LASTEXITCODE -ne 0) { throw 'Could not fetch the GitHub repository.' }
git reset --mixed origin/main
if ($LASTEXITCODE -ne 0) { throw 'Could not align the commit history.' }
git add -A
Write-Host 'Summary of the pending changes:' -ForegroundColor Cyan
git diff --cached --stat
Write-Host 'Verify these changes before uploading.' -ForegroundColor Yellow
$answer = Read-Host 'Push these files to GitHub main? (type YES)'
if ($answer -cne 'YES') { Write-Host 'Cancelled. Nothing was pushed.'; exit 0 }
git diff --cached --quiet
if ($LASTEXITCODE -eq 0) { Write-Host 'There are no changes to publish.'; exit 0 }
git commit -m 'Simplify document validation and add G L Bajaj source packets'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed.' }
git push -u origin HEAD:main
if ($LASTEXITCODE -ne 0) { throw 'Push failed. Check permissions or fetch again; do NOT use force push.' }
Write-Host 'Published. Render auto-deploy should follow GitHub main.' -ForegroundColor Green
