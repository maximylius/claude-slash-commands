---
description: Save the current conversation context to a Notion subpage under "Claude Contexts Page". Use `:long` for detailed, `:medium` for balanced, or `:short` for lean mode. Use `:new` to always create a new page, `:overwrite` to explicitly overwrite an active context.
---

## Step 1: Parse arguments

Scan `$ARGUMENTS` for `:` tokens:
- `:long` / `:medium` / `:short` → **mode**
- `:new` → **behavior = NEW** · `:overwrite` → **behavior = OVERWRITE** · neither → **behavior = AUTO**
- Remaining non-`:` text → optional **name**; unrecognized `:` tokens → ignore

## Step 2: Title

Derive the **base title**: use given name, or a 3–6 word title from the conversation.
The **full title** used for the Notion page is always: `<base title> – YY-MM-DD HH:MM` (current local date/time).

## Step 3: Target page

**Build `active`**: collect every `/restorecontext` load event (page ID + title), remove any subsequently `/unloadcontext`-ed, deduplicate by page ID. Prior `/storecontext` saves keep a page in `active`.

| `active` count | AUTO | OVERWRITE (explicit) |
|---|---|---|
| 0 | → Notion search | → Notion search |
| 1 | Overwrite it; inherit mode from its `Parameters:` line | Overwrite it; inherit mode from its `Parameters:` line |
| 2+ | Create new; tell user "Multiple active — use `:overwrite` to choose" | List active contexts numbered, ask which to overwrite, wait |

**behavior = NEW** → skip to Step 5b.

**Notion search** (active = 0): `notion-search` query = base title, query_type = "internal", page_url = "https://www.notion.so/31fcdf456c4180fe869ee69ed80761f4". Match any child of `31fcdf456c4180fe869ee69ed80761f4` whose title starts with the base title (case-insensitive).
- **Match found** → `notion-fetch` it. Same context? **Yes** → overwrite (5a), inherit `Parameters:` mode. **No** → create new (5b). **Unclear** → show date + one-sentence summary, ask user, wait.
- **No match** → create new (5b).

If mode still UNSPECIFIED after all above: set MEDIUM.

## Step 4: Compose summary

If a context was restored then unloaded this session, treat its content as invisible — draw only from actual conversation turns.

**First line of every summary must be exactly:** `Parameters: :<mode>` (e.g. `Parameters: :long`)

**SHORT** (~150 words max):
- **Goal** — one sentence
- **State** — one sentence
- **Next** — 1–3 bullets

**MEDIUM** (~300–500 words):
- **Project / Task** · **Current State** · **Key Decisions** · **Open Items / Next Steps** · **Important Details** (paths, IDs, links, snippets)

**LONG** (800+ words, thoroughness over brevity):
- **Project / Task** (full scope) · **Current State** (detailed) · **Key Decisions** (rationale + alternatives) · **Open Items** (prioritized) · **Important Details** (all paths, IDs, endpoints, config, snippets, errors) · **Context & Assumptions**

## Step 5a: Overwrite

1. `notion-update-page`: page_id = target, command = "update_properties", properties = {"title": full title (base title + current date)}
2. `notion-update-page`: page_id = target, command = "replace_content", new_str = summary

## Step 5b: Create

`notion-create-pages`: parent = `{"type":"page_id","page_id":"31fcdf45-6c41-80fe-869e-e69ed80761f4"}`, title = full title, content = summary

## Step 6: Confirm

Report: created/updated · mode used (note if inherited) · full title · Notion page URL
