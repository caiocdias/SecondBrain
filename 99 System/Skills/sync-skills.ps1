# Mantém ~/.claude/skills/ apontando para as skills versionadas neste diretório do vault
# e registra em plugins.txt os plugins instalados pelo usuário.
# Versão Windows de sync-skills.sh, com as mesmas regras; usa junctions, que não exigem administrador.
# Executado pelos hooks SessionStart e SessionEnd de ~/.claude/settings.json; pode ser rodado à mão:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<vault>\99 System\Skills\sync-skills.ps1"
#
# 1. Skill nova (ou plugin local criado com `claude plugin init`) instalada ou criada diretamente
#    em ~/.claude/skills/ é movida para cá e substituída por um link.
# 2. Skill criada aqui sem link em ~/.claude/skills/ ganha o link.
# 3. Links para skills removidas daqui são apagados.
# 4. Plugin de marketplace instalado no escopo de usuário e ausente de plugins.txt é acrescentado.
#    O registro só cresce: remoções são feitas à mão.
#
# 5. ~/.claude/agents/second-brain-souls é um único link para 99 System/Souls/agents (as souls do vault).
#    Link para outro lugar ou diretório real nesse nome é conflito e não é alterado.
#
# ~/.claude/skills/synced/ (skills sincronizadas do claude.ai) é gerenciado pelo Claude Code e fica de fora.

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$VaultSkills = $PSScriptRoot
$ConfigDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
$UserSkills = Join-Path $ConfigDir 'skills'
$PluginsFile = Join-Path $VaultSkills 'plugins.txt'
$VaultSouls = Join-Path (Split-Path -Parent $VaultSkills) 'Souls\agents'
$SoulsLink = Join-Path (Join-Path $ConfigDir 'agents') 'second-brain-souls'
$OnWindows = ($PSVersionTable.PSEdition -eq 'Desktop') -or $IsWindows
$Utf8 = New-Object Text.UTF8Encoding $false

function Test-Link($item) { [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint) }

function Test-SkillDir($path) {
  (Test-Path -LiteralPath (Join-Path $path 'SKILL.md')) -or
  (Test-Path -LiteralPath (Join-Path $path '.claude-plugin\plugin.json'))
}

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

function Read-Json($path) {
  if (-not (Test-Path -LiteralPath $path)) { return $null }
  try { Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $null }
}

New-Item -ItemType Directory -Force -Path $UserSkills | Out-Null
$moved = @()
$linked = @()
$conflicts = @()
$failed = @()
$registered = @()

foreach ($item in Get-ChildItem -LiteralPath $UserSkills -Directory -Force) {
  if ($item.Name -eq 'synced' -or $item.Name.StartsWith('.')) { continue }
  if (Test-Link $item) { continue }
  if (-not (Test-SkillDir $item.FullName)) { continue }
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
  if (-not (Test-SkillDir $dir.FullName)) { continue }
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

$soulsLinked = $false
if (Test-Path -LiteralPath $VaultSouls) {
  $existing = Get-Item -LiteralPath $SoulsLink -Force -ErrorAction SilentlyContinue
  if ($existing) {
    if (-not (Test-Link $existing) -or ((Get-LinkTarget $existing) -ne $VaultSouls)) { $conflicts += 'agents/second-brain-souls' }
  } else {
    try {
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $SoulsLink) | Out-Null
      New-SkillLink $SoulsLink $VaultSouls
      $soulsLinked = $true
    } catch { $failed += 'agents/second-brain-souls' }
  }
}

$installed = Read-Json (Join-Path $ConfigDir 'plugins\installed_plugins.json')
$known = Read-Json (Join-Path $ConfigDir 'plugins\known_marketplaces.json')
if ($installed -and $installed.plugins) {
  $listed = @()
  if (Test-Path -LiteralPath $PluginsFile) {
    $listed = @(Get-Content -LiteralPath $PluginsFile -Encoding UTF8 |
      Where-Object { $_ -and -not $_.StartsWith('#') } | ForEach-Object { ($_ -split ' ', 2)[0] })
  }
  foreach ($prop in $installed.plugins.PSObject.Properties) {
    $id = $prop.Name
    if ($id.EndsWith('@skills-dir') -or $listed -contains $id) { continue }
    if (-not (@($prop.Value) | Where-Object { $_.scope -eq 'user' })) { continue }
    $origin = ''
    $marketplace = ($id -split '@')[-1]
    if ($known -and $known.PSObject.Properties[$marketplace]) {
      $source = $known.$marketplace.source
      foreach ($field in 'repo', 'url', 'path', 'package') {
        if ($source.$field) { $origin = $source.$field; break }
      }
    }
    if (-not (Test-Path -LiteralPath $PluginsFile)) {
      $header = "# Plugins do Claude Code registrados no Second Brain (escopo de usuário).`n" +
        "# Uma linha por plugin: <plugin>@<marketplace> <origem do marketplace>.`n" +
        "# sync-skills acrescenta plugins novos; remoções são manuais. Reinstalação: 99 System/AI/setup.md.`n"
      [IO.File]::WriteAllText($PluginsFile, $header, $Utf8)
    }
    [IO.File]::AppendAllText($PluginsFile, ("$id $origin".TrimEnd() + "`n"), $Utf8)
    $listed += $id
    $registered += $id
  }
}

$msg = @()
if ($moved) { $msg += "Skills movidas para o Second Brain: $($moved -join ' ')." }
if ($linked) { $msg += "Skills do Second Brain ativadas: $($linked -join ' ')." }
if ($soulsLinked) { $msg += "Souls do Second Brain ativadas." }
if ($registered) { $msg += "Plugins registrados no Second Brain: $($registered -join ' ')." }
if ($conflicts) { $msg += "Conflito de nome entre ~/.claude/skills e o vault (resolver à mão): $($conflicts -join ' ')." }
if ($failed) { $msg += "Falha ao sincronizar: $($failed -join ' ')." }
if ($msg) { @{ systemMessage = ($msg -join ' ') } | ConvertTo-Json -Compress }
exit 0
