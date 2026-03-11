---
description: Push slash command changes to GitHub and sync all command files to Notion
---

## Step 1: Check for changes

Run: `git -C ~/.claude/commands status --short`

If the output is empty (nothing staged or unstaged), report "Nothing to commit." and skip to Step 3.

## Step 2: Commit and push to GitHub

Run the following in sequence:
```
git -C ~/.claude/commands add *.md
git -C ~/.claude/commands commit -m "Update slash commands"
git -C ~/.claude/commands push
```

Report the files committed and the push result.

## Step 3: Sync all .md files to Notion

Fetch the Notion parent page to discover existing subpages and their IDs:
`notion-fetch` id = "https://www.notion.so/31fcdf456c418052b4dfe75bfb9290eb"

For each `.md` file in `~/.claude/commands/`:

1. Read the file
2. Strip the YAML frontmatter block (everything between the opening and closing `---`)
3. Match the filename stem (e.g. `ctxload`) case-insensitively to a subpage title from the parent page
4. If a match is found: call `notion-update-page` with `command = "replace_content"` using the stripped body as `new_str`
5. If no match: call `notion-create-pages` under parent page id `31fcdf456c418052b4dfe75bfb9290eb` with the filename stem as title and the body as content

Report which Notion pages were updated or created.
