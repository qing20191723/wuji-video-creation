[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$testRoot = Join-Path $repositoryRoot ('tmp\sync-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
$syncScript = Join-Path $PSScriptRoot 'sync-film-skill.ps1'
$parameters = @{
    Target = 'All'
    CodexDestination = Join-Path $testRoot 'codex'
    GrokDestination = Join-Path $testRoot 'grok'
    HermesDestination = Join-Path $testRoot 'hermes'
    BackupRoot = Join-Path $testRoot 'backups'
}
& $syncScript @parameters
& $syncScript @parameters -Check
$installed = Join-Path $parameters.CodexDestination 'SKILL.md'
Set-Content -LiteralPath $installed -Value 'previous installation'
& $syncScript @parameters
$backups = @(Get-ChildItem -LiteralPath $parameters.BackupRoot -Directory -Filter 'codex.backup-*')
if ($backups.Count -ne 1 -or (Get-Content -LiteralPath (Join-Path $backups[0].FullName 'SKILL.md') -Raw).Trim() -ne 'previous installation') {
    throw 'Changed installation backup was not preserved.'
}
$extra = Join-Path $parameters.CodexDestination 'unrelated-user-file.txt'
Set-Content -LiteralPath $extra -Value 'keep this file'
$rejected = $false
try { & $syncScript @parameters } catch { $rejected = $true }
if (-not $rejected -or (Get-Content -LiteralPath $extra -Raw).Trim() -ne 'keep this file') {
    throw 'Unexpected file guard failed.'
}
$rejected = $false
try { & $syncScript -Target Codex -CodexDestination (Join-Path $repositoryRoot 'skills') } catch { $rejected = $true }
if (-not $rejected) { throw 'Overlapping source destination was accepted.' }
Write-Output 'Sync tests passed: initial install, Junction, read-only hash check, backup, unknown-file and source-overlap guards.'
Write-Output "Isolated evidence retained under $testRoot"
