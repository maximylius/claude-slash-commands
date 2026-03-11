#!/usr/bin/env python3
"""Sync markdown command files to Notion subpages on push."""

import os
import re
import sys
from pathlib import Path
from notion_client import Client

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "31fcdf456c418052b4dfe75bfb9290eb")

notion = Client(auth=NOTION_TOKEN)

NOTION_CODE_LANGS = {
    "bash", "c", "c++", "c#", "css", "dart", "docker", "elixir", "go",
    "graphql", "html", "java", "javascript", "json", "kotlin", "latex",
    "markdown", "mermaid", "objective-c", "perl", "php", "plain text",
    "powershell", "python", "r", "ruby", "rust", "scala", "shell",
    "sql", "swift", "typescript", "xml", "yaml",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rich_text(text: str, max_len: int = 2000) -> list:
    """Split text into rich_text chunks (Notion limit: 2000 chars each)."""
    chunks = []
    while text:
        chunks.append({"type": "text", "text": {"content": text[:max_len]}})
        text = text[max_len:]
    return chunks or [{"type": "text", "text": {"content": ""}}]


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Strip YAML frontmatter and return (metadata, body)."""
    import yaml
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(content[3:end].strip()) or {}
                return fm, content[end + 3:].strip()
            except yaml.YAMLError:
                pass
    return {}, content


def all_children(block_id: str) -> list:
    """Fetch all children of a block, handling pagination."""
    results = []
    cursor = None
    while True:
        kwargs = {"block_id": block_id}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = notion.blocks.children.list(**kwargs)
        results.extend(resp["results"])
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]
    return results


# ---------------------------------------------------------------------------
# Markdown → Notion blocks
# ---------------------------------------------------------------------------

def md_to_blocks(md: str) -> list:
    """Convert markdown to a list of Notion block dicts (best-effort)."""
    blocks = []
    lines = md.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            lang = line[3:].strip().lower() or "plain text"
            if lang not in NOTION_CODE_LANGS:
                lang = "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            # Split code if longer than 2000 chars
            while code_text:
                chunk, code_text = code_text[:2000], code_text[2000:]
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}],
                        "language": lang,
                    },
                })
            i += 1
            continue

        # Table — collect rows, render as paragraph (Notion tables require exact col count)
        if line.strip().startswith("|") and "|" in line:
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and "|" in lines[i]:
                row = lines[i].strip()
                if not re.match(r"^\|[-| :]+\|$", row):   # skip separator
                    cells = [c.strip() for c in row.split("|")[1:-1]]
                    rows.append(" | ".join(cells))
                i += 1
            if rows:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": rich_text("\n".join(rows))},
                })
            continue

        # Headings
        if line.startswith("### "):
            blocks.append({"object": "block", "type": "heading_3",
                            "heading_3": {"rich_text": rich_text(line[4:])}})
        elif line.startswith("## "):
            blocks.append({"object": "block", "type": "heading_2",
                            "heading_2": {"rich_text": rich_text(line[3:])}})
        elif line.startswith("# "):
            blocks.append({"object": "block", "type": "heading_1",
                            "heading_1": {"rich_text": rich_text(line[2:])}})

        # Bullet list
        elif line.startswith("- ") or line.startswith("* "):
            blocks.append({"object": "block", "type": "bulleted_list_item",
                            "bulleted_list_item": {"rich_text": rich_text(line[2:])}})

        # Numbered list
        elif re.match(r"^\d+\. ", line):
            text = re.sub(r"^\d+\. ", "", line)
            blocks.append({"object": "block", "type": "numbered_list_item",
                            "numbered_list_item": {"rich_text": rich_text(text)}})

        # Non-empty paragraph
        elif line.strip():
            blocks.append({"object": "block", "type": "paragraph",
                            "paragraph": {"rich_text": rich_text(line)}})

        i += 1

    return blocks


# ---------------------------------------------------------------------------
# Notion operations
# ---------------------------------------------------------------------------

def get_subpages() -> dict[str, str]:
    """Return {title_lower: page_id} for all child_page blocks under parent."""
    pages = {}
    for block in all_children(PARENT_PAGE_ID):
        if block["type"] == "child_page":
            title = block["child_page"]["title"]
            pages[title.lower()] = block["id"]
    return pages


def replace_page_content(page_id: str, blocks: list, description: str | None) -> None:
    """Delete all existing blocks and append new ones."""
    for block in all_children(page_id):
        notion.blocks.delete(block_id=block["id"])

    all_blocks = []
    if description:
        all_blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": rich_text(description),
                "icon": {"type": "emoji", "emoji": "💡"},
            },
        })
    all_blocks.extend(blocks)

    # Notion API: max 100 children per request
    for start in range(0, max(len(all_blocks), 1), 100):
        notion.blocks.children.append(
            block_id=page_id,
            children=all_blocks[start:start + 100],
        )


def create_subpage(title: str, blocks: list, description: str | None) -> str:
    page = notion.pages.create(
        parent={"page_id": PARENT_PAGE_ID},
        properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
    )
    replace_page_content(page["id"], blocks, description)
    return page["id"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    repo_root = Path(__file__).parent.parent
    md_files = sorted(repo_root.glob("*.md"))

    if not md_files:
        print("No .md files found.")
        return

    print(f"Found {len(md_files)} file(s): {[f.name for f in md_files]}")
    subpages = get_subpages()
    print(f"Notion subpages: {list(subpages.keys())}")

    for md_file in md_files:
        stem = md_file.stem.lower()
        content = md_file.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)
        description = frontmatter.get("description")
        blocks = md_to_blocks(body)

        if stem in subpages:
            page_id = subpages[stem]
            print(f"  Updating  '{md_file.stem}' → {page_id}")
            replace_page_content(page_id, blocks, description)
        else:
            print(f"  Creating  '{md_file.stem}'")
            new_id = create_subpage(md_file.stem, blocks, description)
            print(f"            → {new_id}")

    print("Sync complete.")


if __name__ == "__main__":
    main()
