[CmdletBinding()]
param(
    [ValidateSet('Codex', 'Grok', 'Hermes', 'All')]
    [string]$Target = 'All',
    [switch]$Check,
    [string]$Destination,
    [string]$CodexDestination,
    [string]$GrokDestination,
    [string]$HermesDestination,
    [string]$HermesDistro = 'Ubuntu-22.04',
    [string]$HermesHome = '$HOME'
)

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = [IO.Path]::GetFullPath((Join-Path $repositoryRoot 'skills\seedance-film-production'))
if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
    throw "Repository Skill source directory not found: $sourcePath"
}

if (-not [string]::IsNullOrWhiteSpace($Destination)) {
    if (($PSBoundParameters.ContainsKey('Target') -and $Target -ne 'Codex') -or
        -not [string]::IsNullOrWhiteSpace($CodexDestination)) {
        throw '-Destination is the legacy Codex-only override; use -Target Codex or -CodexDestination.'
    }
    $Target = 'Codex'
    $CodexDestination = $Destination
}

$userProfilePath = [Environment]::GetFolderPath('UserProfile')
if ([string]::IsNullOrWhiteSpace($CodexDestination)) {
    $CodexDestination = Join-Path $userProfilePath '.codex\skills\seedance-film-production'
}
if ([string]::IsNullOrWhiteSpace($GrokDestination)) {
    $GrokDestination = Join-Path $userProfilePath '.grok\skills\seedance-film-production'
}
if ([string]::IsNullOrWhiteSpace($HermesDestination)) {
    $hermesRelative = $HermesHome.Trim('/').Replace('/', '\')
    $HermesDestination = "\\wsl.localhost\$HermesDistro\$hermesRelative\.hermes\skills\creative\seedance-film-production"
}

$codexPath = [IO.Path]::GetFullPath($CodexDestination)
$grokPath = [IO.Path]::GetFullPath($GrokDestination)
$hermesPath = [IO.Path]::GetFullPath($HermesDestination)

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

function Assert-SafeDestination {
    param([Parameter(Mandatory)][string]$Path)

    if ($Path.TrimEnd('\', '/') -eq $sourcePath.TrimEnd('\', '/')) {
        throw "Installed destination must not be the repository source: $Path"
    }
}

function Sync-PhysicalSkill {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][hashtable]$SourceManifest
    )

    Assert-SafeDestination -Path $Path
    $existing = Get-SkillManifest -Root $Path
    $extra = @($existing.Keys | Where-Object { -not $SourceManifest.ContainsKey($_) } | Sort-Object)
    if ($extra.Count -gt 0) {
        throw "$Name destination contains unexpected files and was not modified: $($extra -join ', ')"
    }

    if (-not $Check) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        foreach ($relative in $SourceManifest.Keys) {
            $sourceFile = Join-Path $sourcePath $relative
            $destinationFile = Join-Path $Path $relative
            $destinationDirectory = Split-Path -Parent $destinationFile
            New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
            Copy-Item -LiteralPath $sourceFile -Destination $destinationFile -Force
        }
    }

    $targetManifest = Get-SkillManifest -Root $Path
    $differences = Compare-SkillManifest -Source $SourceManifest -Target $targetManifest
    if ($differences.Count -gt 0) {
        $differences | ForEach-Object { Write-Error "$Name`: $_" }
        throw "$Name installed Skill differs in $($differences.Count) item(s)."
    }
    Write-Output "$Name verified: $($SourceManifest.Count) files match SHA-256 at $Path"
}

function Sync-GrokJunction {
    param([Parameter(Mandatory)][hashtable]$SourceManifest)

    Assert-SafeDestination -Path $grokPath
    $item = Get-Item -LiteralPath $grokPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) {
        if ($Check) {
            throw "Grok Junction is missing: $grokPath"
        }
        $parent = Split-Path -Parent $grokPath
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        New-Item -ItemType Junction -Path $grokPath -Target $codexPath | Out-Null
        $item = Get-Item -LiteralPath $grokPath -Force
    }

    if ($item.LinkType -ne 'Junction') {
        throw "Grok destination must be a Junction and was not modified: $grokPath"
    }
    $junctionTargets = @($item.Target)
    if ($junctionTargets.Count -ne 1) {
        throw "Grok Junction must have exactly one target: $grokPath"
    }
    $actualTarget = [IO.Path]::GetFullPath([string]$junctionTargets[0]).TrimEnd('\', '/')
    $expectedTarget = $codexPath.TrimEnd('\', '/')
    if (-not $actualTarget.Equals($expectedTarget, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Grok Junction points to '$actualTarget', expected '$expectedTarget'. It was not modified."
    }

    $targetManifest = Get-SkillManifest -Root $grokPath
    $differences = Compare-SkillManifest -Source $SourceManifest -Target $targetManifest
    if ($differences.Count -gt 0) {
        $differences | ForEach-Object { Write-Error "Grok`: $_" }
        throw "Grok installed Skill differs in $($differences.Count) item(s)."
    }
    Write-Output "Grok verified: Junction targets Codex and $($SourceManifest.Count) files match SHA-256 at $grokPath"
}

$sourceManifest = Get-SkillManifest -Root $sourcePath
if ($sourceManifest.Count -eq 0) {
    throw 'Repository Skill source directory contains no syncable files.'
}

$selected = if ($Target -eq 'All') { @('Codex', 'Grok', 'Hermes') } else { @($Target) }
foreach ($name in $selected) {
    switch ($name) {
        'Codex' { Sync-PhysicalSkill -Name 'Codex' -Path $codexPath -SourceManifest $sourceManifest }
        'Grok' {
            if (-not (Test-Path -LiteralPath $codexPath -PathType Container)) {
                throw "Codex installed Skill must exist before Grok can link to it: $codexPath"
            }
            Sync-GrokJunction -SourceManifest $sourceManifest
        }
        'Hermes' { Sync-PhysicalSkill -Name 'Hermes' -Path $hermesPath -SourceManifest $sourceManifest }
    }
}

$operation = if ($Check) { 'check' } else { 'sync' }
Write-Output "Skill $operation completed for target: $Target"
Write-Output "Source: $sourcePath"
