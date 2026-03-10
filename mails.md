---
description: Open email search interface
---

You are starting the email search session. Follow these steps exactly:

1. If `thunderbird-email` tools are not available in this session, stop immediately and say:
   "Not available on mobile app. This command requires Claude Desktop with the Thunderbird MCP running."
   Do NOT proceed further.

2. Call `thunderbird-email:read_file` with filename `artifact.html` and display the result as an HTML artifact.

3. If the `read_file` tool returns an error, stop and say:
   "The thunderbird-email MCP server isn't responding. Please restart Claude Desktop and try again."
   Do NOT fetch emails as a fallback.

4. After displaying the artifact, say exactly:
   "Accounts and folders shown above. Defaults are pre-selected — adjust if needed, then tell me what you're looking for."

5. Wait for the user's question. Do NOT fetch emails until the user asks something.
