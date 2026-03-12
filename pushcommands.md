---
description: Push slash command changes to GitHub and sync all command files to Notion
---

## Step 0: Parse arguments

Check `$ARGUMENTS` for `:all`. If present, set **sync_all = true**, otherwise **sync_all = false**.

## Step 1: Check for changes

Run: `git -C ~/.claude/commands status --short`

If the output is empty (nothing staged or unstaged):
- Report "Nothing to commit."
- If **sync_all = false**: report "Notion already up to date. Use `:all` to force-sync all pages." Stop.
- If **sync_all = true**: skip Step 2, go to Step 3 using all `.md` files as the sync list.

## Step 2: Commit and push to GitHub

Run the following in sequence:
```
git -C ~/.claude/commands add *.md
git -C ~/.claude/commands commit -m "Update slash commands"
git -C ~/.claude/commands push
```

Report the files committed and the push result.

Then run: `git -C ~/.claude/commands show --name-only --format="" HEAD`

This lists the `.md` files in the commit. Use these as the **sync list** (the files to sync to Notion).

If **sync_all = true**, override the sync list with all `.md` files in `~/.claude/commands/`.

## Step 3: Sync changed .md files to Notion

Fetch the Notion parent page to discover existing subpages and their IDs:
`notion-fetch` id = "https://www.notion.so/31fcdf456c418052b4dfe75bfb9290eb"

For each `.md` file in the **sync list**:

1. Read the file
2. Strip the YAML frontmatter block (everything between the opening and closing `---`)
3. Match the filename stem (e.g. `ctxload`) case-insensitively to a subpage title from the parent page
4. If a match is found: call `notion-update-page` with `command = "replace_content"` using the stripped body as `new_str`
5. If no match: call `notion-create-pages` under parent page id `31fcdf456c418052b4dfe75bfb9290eb` with the filename stem as title and the body as content

Report which Notion pages were updated or created.

## Step 4: Stamp each synced subpage title with the current timestamp

After each `notion-update-page` or `notion-create-pages` call in Step 3, immediately call:

```
notion-update-page
  page_id = <the page just updated or created>
  command = "update_properties"
  properties = { "title": "<commandname> YY-MM-DD HH:MM" }
```

- Replace `<commandname>` with the filename stem (e.g. `mails`)
- Replace `YY-MM-DD HH:MM` with the **current UTC time** at the moment of the push (e.g. `26-03-12 14:30`)
- Example result: `mails 26-03-12 14:30`

Report the new title set for each page.
