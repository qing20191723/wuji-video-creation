[CmdletBinding()]
param(
    [switch]$Check,
    [string]$Destination
)

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$sourcePath = Join-Path $repositoryRoot 'skills\seedance-film-production'
if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
    throw "找不到仓库 Skill 源目录：$sourcePath"
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
            $relative = [IO.Path]::GetRelativePath($Root, $_.FullName).Replace('\', '/')
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
            $differences.Add("缺少：$relative")
        }
        elseif ($Source[$relative] -ne $Target[$relative]) {
            $differences.Add("内容不同：$relative")
        }
    }
    foreach ($relative in $Target.Keys | Sort-Object) {
        if (-not $Source.ContainsKey($relative)) {
            $differences.Add("目标存在额外文件：$relative")
        }
    }
    return $differences
}

$sourceManifest = Get-SkillManifest -Root $sourcePath
if ($sourceManifest.Count -eq 0) {
    throw "仓库 Skill 源目录没有可同步文件。"
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
    throw "仓库版与本机安装版不一致，共 $($differences.Count) 项。"
}

Write-Output "Skill 同步校验通过：$($sourceManifest.Count) 个文件，SHA-256 全部一致。"
Write-Output "源目录：$sourcePath"
Write-Output "目标目录：$destinationPath"
