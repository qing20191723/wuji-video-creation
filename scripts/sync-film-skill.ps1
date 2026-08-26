[CmdletBinding()]
param(
    [switch]$Check,
    [string]$Destination
)

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $repositoryRoot 'skills\seedance-film-production'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
    throw "Repository Skill source directory not found: $sourcePath"
}

if ([string]::IsNullOrWhiteSpace($Destination)) {
    $Destination = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills\seedance-film-production'
}
$destinationPath = [IO.Path]::GetFullPath($Destination)
$sourcePath = [IO.Path]::GetFullPath($sourcePath)

function Get-SkillManifest {
    param([Parameter(Mandatory)][string]$Root)

    $manifest = @{}
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        return $manifest
    }

    Get-ChildItem -LiteralPath $Root -Recurse -File |
        Where-Object {
            $_.FullName -notmatch '[\\/]__pycache__[\\/]' -and
            $_.Extension -ne '.pyc'
        } |
        ForEach-Object {
            $relative = $_.FullName.Substring($Root.TrimEnd('\', '/').Length).TrimStart('\', '/').Replace('\', '/')
            $manifest[$relative] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    return $manifest
}

function Compare-SkillManifest {
    param(
        [Parameter(Mandatory)][hashtable]$Source,
        [Parameter(Mandatory)][hashtable]$Target
    )

    $differences = [System.Collections.Generic.List[string]]::new()
    foreach ($relative in $Source.Keys | Sort-Object) {
        if (-not $Target.ContainsKey($relative)) {
            $differences.Add("Missing: $relative")
        }
        elseif ($Source[$relative] -ne $Target[$relative]) {
            $differences.Add("Content differs: $relative")
        }
    }
    foreach ($relative in $Target.Keys | Sort-Object) {
        if (-not $Source.ContainsKey($relative)) {
            $differences.Add("Extra target file: $relative")
        }
    }
    return $differences
}

$sourceManifest = Get-SkillManifest -Root $sourcePath
if ($sourceManifest.Count -eq 0) {
    throw "Repository Skill source directory contains no syncable files."
}

if (-not $Check) {
    New-Item -ItemType Directory -Path $destinationPath -Force | Out-Null
    foreach ($relative in $sourceManifest.Keys) {
        $sourceFile = Join-Path $sourcePath $relative
        $destinationFile = Join-Path $destinationPath $relative
        $destinationDirectory = Split-Path -Parent $destinationFile
        New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
        Copy-Item -LiteralPath $sourceFile -Destination $destinationFile -Force
    }
}

$targetManifest = Get-SkillManifest -Root $destinationPath
$differences = Compare-SkillManifest -Source $sourceManifest -Target $targetManifest
if ($differences.Count -gt 0) {
    $differences | ForEach-Object { Write-Error $_ }
    throw "Repository and installed Skill differ in $($differences.Count) item(s)."
}

Write-Output "Skill sync verified: $($sourceManifest.Count) files have matching SHA-256 hashes."
Write-Output "Source: $sourcePath"
Write-Output "Destination: $destinationPath"
