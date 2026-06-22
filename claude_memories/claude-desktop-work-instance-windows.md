---
name: claude-desktop-work-instance-windows
description: How the personal+work dual Claude Desktop / CLI isolation is set up on this Windows machine
metadata:
  node_type: memory
  type: reference
  originSessionId: 326adcc3-4894-4555-83db-904aa00655eb
---

Claude Desktop on this machine is a **sideloaded MSIX** (SignatureKind Developer), installed via **winget/UniGetUI**. PackageFamilyName `Claude_pzs8sxrjxfjjc`; exe at version-stamped `C:\Program Files\WindowsApps\Claude_<ver>_x64__pzs8sxrjxfjjc\app\Claude.exe`. The **direct Squirrel `.exe`** build (claude.ai/download) does NOT install here — the 6.7 MB stub exits without downloading, no `%LOCALAPPDATA%\AnthropicClaude` is ever created, and winget/UniGetUI always pulls the MSIX. So there is only ever the one MSIX build.

**KEY (verified):** launching that MSIX exe **directly** (not via the Store tile) DOES honor Electron `--user-data-dir` — it spawns a fully separate instance on its own profile (Claude-Work filled with files; child procs all carried the flag). Only **tile / AppsFolder activation drops argv**, which is why I first thought MSIX couldn't do it. So no second install is needed.

Setup — the helper scripts + a `README.md` live in the folder **`<OneDrive Desktop>\Claude-Dual-Setup\`** (`setup-claude-work.ps1`, `claude-work-launch.ps1`, `claude-work-login.ps1`, `README.md`). `setup-claude-work.ps1` is self-locating via `$PSScriptRoot`, so the folder can be moved/renamed and re-running regenerates the launcher + re-points shortcuts beside itself (also how to deploy on another machine: copy folder, run setup, run login). The "Claude (Work)" shortcut fires that folder's `claude-work-launch.ps1` on every click, so OneDrive must keep it hydrated (online).
- **Personal** = normal Claude window (data `%APPDATA%\Claude`). **Work** = `--user-data-dir=%LOCALAPPDATA%\Claude-Work`.
- `claude-work-launch.ps1` resolves the current versioned exe via the stable PFN each run (survives updates) and `Start-Process`es it with the flag.
- Shortcuts (Desktop + Start Menu): **"Claude (Work)"** → `powershell -WindowStyle Hidden -File <Desktop>\claude-work-launch.ps1`; **"Claude (Personal)"** → `explorer shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude` (proper MSIX activation = package identity, default profile).
- `setup-claude-work.ps1` (idempotent) recreates launcher+shortcuts+CLI func; re-run after a major Claude update.

**Login gotcha:** `claude://` is registered in `HKCU\Software\Classes\claude\shell\open\command` as `"<exe>" "%1"` on the DEFAULT profile, so a work sign-in's deep-link callback would be captured by the personal instance. `claude-work-login.ps1` temporarily repoints `claude://` at `Claude-Work` during sign-in (quit personal first), then restores it.

**Work CLI account** = function `claude-work` (sets `CLAUDE_CONFIG_DIR=$HOME\.claude-work`) vs default `~\.claude`; CLI at `~\.local\bin\claude.exe`. Note `$PROFILE` and Desktop are OneDrive-redirected (`...\OneDrive - Agency for Science, Technology and Research\...`); the function lands only in the profile of whichever PowerShell edition ran setup. Direct-exe launch + `--user-data-dir` are stable but undocumented.

**Usage (user's choice, 2026-06-22) — labels are INVERTED vs actual use:** the user runs the DEFAULT/AUMID instance ("Claude (Personal)" shortcut, `%APPDATA%\Claude`, plain `claude` CLI) as their **WORK** account (machine was already signed into work), and the new Claude-Work-profile instance ("Claude (Work)" shortcut, `claude-work` CLI) as **PERSONAL**. So "Work"/"Personal" naming on shortcuts/dirs/CLI is backwards from reality (functionality unaffected — isolation is by data dir). For the personal (Claude-Work) instance's first sign-in, run `claude-work-login.ps1` and sign in with the PERSONAL account; when it says "quit personal Claude" it means quit the default-profile (=work) window. Work side needs no login helper (default profile gets `claude://` natively). Offered to flip the labels; user said leave it for now.
