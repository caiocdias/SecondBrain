# Mantém ~/.claude/skills/ apontando para as skills versionadas neste diretório do vault.
# Versão Windows de sync-skills.sh, com as mesmas regras; usa junctions, que não exigem administrador.
# Executado pelos hooks SessionStart e SessionEnd de ~/.claude/settings.json; pode ser rodado à mão:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<vault>\99 System\Skills\sync-skills.ps1"
#
# 1. Skill nova instalada ou criada diretamente em ~/.claude/skills/ é movida para cá e
#    substituída por um link.
# 2. Skill criada aqui sem link em ~/.claude/skills/ ganha o link.
# 3. Links para skills removidas daqui são apagados.
#
# ~/.claude/skills/synced/ (skills sincronizadas do claude.ai) é gerenciado pelo Claude Code e fica de fora.

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$VaultSkills = $PSScriptRoot
$ConfigDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
$UserSkills = Join-Path $ConfigDir 'skills'
$OnWindows = ($PSVersionTable.PSEdition -eq 'Desktop') -or $IsWindows

function Test-Link($item) { [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint) }

function Get-LinkTarget($item) {
  $target = @($item.Target)[0]
  if ($target) { $target.TrimEnd('\', '/') }
}

function New-SkillLink($link, $target) {
  $type = if ($OnWindows) { 'Junction' } else { 'SymbolicLink' }
  New-Item -ItemType $type -Path $link -Target $target -ErrorAction Stop | Out-Null
}

# Apaga só o link, nunca o conteúdo do destino.
function Remove-SkillLink($link) {
  if ($OnWindows) {
    try { [IO.Directory]::Delete($link, $false) } catch { cmd /c rmdir "$link" | Out-Null }
  } else {
    [IO.File]::Delete($link)
  }
}

New-Item -ItemType Directory -Force -Path $UserSkills | Out-Null
$moved = @()
$linked = @()
$conflicts = @()
$failed = @()

foreach ($item in Get-ChildItem -LiteralPath $UserSkills -Directory -Force) {
  if ($item.Name -eq 'synced' -or $item.Name.StartsWith('.')) { continue }
  if (Test-Link $item) { continue }
  if (-not (Test-Path -LiteralPath (Join-Path $item.FullName 'SKILL.md'))) { continue }
  $dest = Join-Path $VaultSkills $item.Name
  if (Test-Path -LiteralPath $dest) { $conflicts += $item.Name; continue }
  try {
    try {
      Move-Item -LiteralPath $item.FullName -Destination $dest -ErrorAction Stop
    } catch {
      # Move-Item não move pastas entre volumes diferentes (vault em D:, perfil em C:).
      Copy-Item -LiteralPath $item.FullName -Destination $dest -Recurse -ErrorAction Stop
      Remove-Item -LiteralPath $item.FullName -Recurse -Force -ErrorAction Stop
    }
    New-SkillLink $item.FullName $dest
    $moved += $item.Name
  } catch {
    $failed += $item.Name
  }
}

foreach ($dir in Get-ChildItem -LiteralPath $VaultSkills -Directory) {
  if (-not (Test-Path -LiteralPath (Join-Path $dir.FullName 'SKILL.md'))) { continue }
  $link = Join-Path $UserSkills $dir.Name
  $existing = Get-Item -LiteralPath $link -Force -ErrorAction SilentlyContinue
  if ($existing) {
    if ((Test-Link $existing) -and ((Get-LinkTarget $existing) -ne $dir.FullName)) { $conflicts += $dir.Name }
    continue
  }
  try { New-SkillLink $link $dir.FullName; $linked += $dir.Name } catch { $failed += $dir.Name }
}

foreach ($item in Get-ChildItem -LiteralPath $UserSkills -Force) {
  if (-not (Test-Link $item)) { continue }
  $target = Get-LinkTarget $item
  if ($target -and -not (Test-Path -LiteralPath $target) -and
      $target.StartsWith($VaultSkills, [StringComparison]::OrdinalIgnoreCase)) {
    Remove-SkillLink $item.FullName
  }
}

$msg = @()
if ($moved) { $msg += "Skills movidas para o Second Brain: $($moved -join ' ')." }
if ($linked) { $msg += "Skills do Second Brain ativadas: $($linked -join ' ')." }
if ($conflicts) { $msg += "Conflito de nome entre ~/.claude/skills e o vault (resolver à mão): $($conflicts -join ' ')." }
if ($failed) { $msg += "Falha ao sincronizar: $($failed -join ' ')." }
if ($msg) { @{ systemMessage = ($msg -join ' ') } | ConvertTo-Json -Compress }
exit 0
