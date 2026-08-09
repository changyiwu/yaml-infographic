[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet("codex", "claude", "opencode", "antigravity", "all")]
    [string[]]$Agent = @("codex"),

    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$source = Join-Path $repoRoot "skills\yaml-infographic"
if (-not (Test-Path -LiteralPath (Join-Path $source "SKILL.md"))) {
    throw "找不到技能來源：$source"
}

$userProfilePath = [Environment]::GetFolderPath("UserProfile")
$targetRoots = [ordered]@{
    codex       = Join-Path $userProfilePath ".codex\skills"
    claude      = Join-Path $userProfilePath ".claude\skills"
    opencode    = Join-Path $userProfilePath ".config\opencode\skills"
    antigravity = Join-Path $userProfilePath ".gemini\config\skills"
}

$selected = if ($Agent -contains "all") {
    @($targetRoots.Keys)
} else {
    @($Agent | Select-Object -Unique)
}

$entries = foreach ($name in $selected) {
    $root = [System.IO.Path]::GetFullPath($targetRoots[$name])
    $destination = [System.IO.Path]::GetFullPath((Join-Path $root "yaml-infographic"))
    $prefix = $root.TrimEnd("\") + "\"
    if (-not $destination.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "不安全的安裝目標：$destination"
    }
    [pscustomobject]@{
        Agent = $name
        Root = $root
        Destination = $destination
    }
}

$collisions = @($entries | Where-Object { Test-Path -LiteralPath $_.Destination })
if ($collisions.Count -gt 0 -and -not $Force) {
    $paths = ($collisions.Destination -join [Environment]::NewLine)
    throw "以下位置已存在 yaml-infographic。確認後以 -Force 重試；舊版會先移到備份資料夾：$([Environment]::NewLine)$paths"
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmssfff"
foreach ($entry in $entries) {
    if ($PSCmdlet.ShouldProcess($entry.Destination, "安裝 yaml-infographic 給 $($entry.Agent)")) {
        New-Item -ItemType Directory -Force -Path $entry.Root | Out-Null
        if (Test-Path -LiteralPath $entry.Destination) {
            $backup = "$($entry.Destination).backup-$timestamp"
            Move-Item -LiteralPath $entry.Destination -Destination $backup
            Write-Output "已備份舊版：$backup"
        }
        Copy-Item -LiteralPath $source -Destination $entry.Destination -Recurse -Force
        Write-Output "已安裝 $($entry.Agent)：$($entry.Destination)"
    }
}
