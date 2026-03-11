---
description: Enable portable path mode — avoid hardcoded usernames in all file paths written this session
---

# portablecode

Activates portable path mode for this session.

## Step 1 — Check for existing username paths in this session

Call `mcp__Desktop_Commander__get_recent_tool_calls` with `maxResults: 100`.

Scan the results for any paths that contain a literal username — i.e. the pattern `C:/Users/<word>/`, `C:\Users\<word>\`, or `/c/Users/<word>/` where `<word>` is a plain word (not a variable like `$env:USERPROFILE`, `$USERPROFILE`, `%USERPROFILE%`, or `~`).

- **No username paths found**: Reply with one line confirming portable path mode is active, then jump to Step 3.
- **Username paths found**: List the affected files and the offending strings, then ask: *"Found hardcoded username paths in N file(s) from this session. Attempt to replace them with portable equivalents?"*

If the user confirms, proceed to Step 2. Otherwise skip to Step 3.

## Step 2 — Fix existing username paths

For each affected file:

1. Read the file.
2. Replace each hardcoded username path using the table below.
3. Write the file back.
4. Report what changed.

| Context | Replace `C:\Users\<name>\...` with |
|---|---|
| Descriptive text / prose | `~\...` |
| PowerShell string or command | `$env:USERPROFILE\...` |
| Bash string or command | `$USERPROFILE/...` or `~/...` |
| CMD / .bat string | `%USERPROFILE%\...` |
| Python source code | `Path.home() / "..."` or `os.path.expanduser("~/...")` |
| Node.js source code | `path.join(os.homedir(), "...")` |
| Tool `path` argument (Desktop Commander tools) | `~\...` *(see caveat)* |

**Caveat — Desktop Commander tool `path` arguments**: Tilde is not resolved reliably in `mcp__Desktop_Commander__*` path arguments on all systems. If a portable path cannot be verified to work, warn the user and leave the path as-is rather than silently breaking it.

**When replacement is not possible**: If a path is in a context where none of the above conventions apply (e.g. an external config format that requires an absolute path, a compiled reference, a URL), do not attempt the replacement. Instead flag the specific location to the user with a brief explanation.

## Step 3 — Session rules (apply for the rest of this session)

From this point forward, never write a path containing a literal Windows username.

| Context | Use instead |
|---|---|
| Descriptive text, prose, code comments | `~\path` or `~/path` |
| PowerShell command strings | `$env:USERPROFILE\path` |
| Bash command strings | `$USERPROFILE/path` or `~/path` |
| CMD / batch | `%USERPROFILE%\path` |
| Python | `Path.home() / "path"` or `os.path.expanduser("~/path")` |
| Node.js | `path.join(os.homedir(), "path")` |
| Desktop Commander tool path args | `~\path` (or resolve at runtime if tilde unreliable) |

Additional rules:
- If a **relative path** (e.g. `./config.json`) is correct and sufficient, prefer it over any home-directory path.
- If a portable path is **not achievable** (platform constraint, external tool requires absolute path, etc.), explain why to the user before using a hardcoded path.
- If the **username is needed at runtime** and cannot be avoided (e.g. constructing a Desktop Commander path inside a command file), obtain it dynamically first:
  ```powershell
  $env:USERPROFILE
  ```
  Then substitute the result into the path.
