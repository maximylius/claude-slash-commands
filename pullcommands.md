---
description: Pull slash commands from GitHub into ~/.claude/commands, initializing git if needed
---

## Step 1: Check if git is initialized

Run: `git -C ~/.claude/commands rev-parse --is-inside-work-tree 2>&1`

- If the output is `true` → repo exists, go to **Path A**.
- If the output contains "not a git repository" or any error → go to **Path B**.

---

## Path A — Repo already initialized (pull)

### A1 — Check for uncommitted local changes

Run: `git -C ~/.claude/commands status --short`

If the output is non-empty (uncommitted changes exist), warn the user:

> "There are local uncommitted changes in `~/.claude/commands`. A pull may create merge conflicts. Proceed?"

Wait for confirmation before continuing.

### A2 — Pull

Run:
```
git -C ~/.claude/commands pull
```

Report the result (files updated or "Already up to date.").

---

## Path B — Not a git repository (initialize)

### B1 — Confirm remote URL

Ask the user:
> "`~/.claude/commands` is not a git repository. Initialize it and pull from GitHub? Default remote: `https://github.com/maximylius/claude-slash-commands.git` — press Enter to confirm or provide a different URL."

If the user provides a different URL, use that. Otherwise use the default above.

### B2 — Warn about existing files

Run: `ls ~/.claude/commands/*.md 2>/dev/null`

If `.md` files already exist in the folder, warn the user:
> "Existing `.md` files in `~/.claude/commands` may be overwritten by files from the remote. Proceed?"

Wait for confirmation.

### B3 — Initialize, add remote, and pull

Run the following in sequence:
```
git -C ~/.claude/commands init
git -C ~/.claude/commands remote add origin <URL>
git -C ~/.claude/commands fetch origin
git -C ~/.claude/commands checkout -b main --track origin/main
```

If the `checkout -b main` step fails (e.g. branch is named `master`), retry with:
```
git -C ~/.claude/commands checkout -b master --track origin/master
```

If files already existed and git reports a conflict (untracked files would be overwritten), run:
```
git -C ~/.claude/commands checkout -f main
```

Report the result and list the pulled `.md` files.
