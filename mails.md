---
description: Open email search interface
---

You are starting the email search session. Follow these steps exactly:

1. Call `thunderbird-email:read_file` with filename `artifact.html` and display the result as an HTML artifact.

2. If the `read_file` tool is unavailable or returns an error, stop and say:
   "The thunderbird-email MCP server isn't responding. Please restart Claude Desktop and try again."
   Do NOT fetch emails as a fallback.

3. After displaying the artifact, say exactly:
   "Accounts and folders shown above. Defaults are pre-selected — adjust if needed, then tell me what you're looking for."

4. Wait for the user's question. Do NOT fetch emails until the user asks something.
