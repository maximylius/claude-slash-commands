---
description: Unload the currently restored context from this conversation session, so subsequent /storecontext calls no longer target it automatically.
---

## Step 1: Find active context

Check session history for the most recently active context (from `/restorecontext` or `/storecontext`). Note its title and page URL. If none: "No context is currently loaded." Stop.

## Step 2: Soft unload

From this point forward:
- Do not use the unloaded page as a save target for `/storecontext`
- When composing future `/storecontext` summaries, treat the unloaded context's content as invisible — summarize only actual conversation turns

## Step 3: Confirm

"Context '[title]' unloaded. Future /storecontext calls will search Notion or create a new page. Its content remains in history but won't be auto-targeted."
