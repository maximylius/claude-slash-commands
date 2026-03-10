---
description: Unload the currently restored context from this conversation session, so subsequent /ctxsave calls no longer target it automatically.
---

## Step 1: Find active context

Check session history for the most recently active context (from `/ctxload` or `/ctxsave`). Note its title and page URL. If none: "No context is currently loaded." Stop.

## Step 2: Soft unload

From this point forward:
- Do not use the unloaded page as a save target for `/ctxsave`
- When composing future `/ctxsave` summaries, treat the unloaded context's content as invisible — summarize only actual conversation turns

## Step 3: Confirm

"Context '[title]' unloaded. Future /ctxsave calls will search Notion or create a new page. Its content remains in history but won't be auto-targeted."
