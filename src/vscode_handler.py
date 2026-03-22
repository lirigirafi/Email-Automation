"""
VS Code Integration module
Handles presentation of drafts and approval workflow in VS Code
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class VSCodeHandler:
    """Manages VS Code integration for draft presentation"""
    
    def __init__(self, draft_output_path: str = "./data/drafts"):
        self.draft_output_path = Path(draft_output_path)
        self.draft_output_path.mkdir(parents=True, exist_ok=True)
        self.pending_approvals = {}
    
    def create_draft_markdown(self, draft: Dict) -> str:
        """
        Create a markdown file for draft presentation
        Returns the file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.draft_output_path / f"draft_{timestamp}.md"
        
        markdown_content = f"""# Email Draft for Approval
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Email
- **From:** {draft.get('original_sender', 'Unknown')}
- **Subject:** {draft.get('original_subject', 'No Subject')}

---

## Your Draft Response

**To:** {draft.get('original_sender', '')}

**Subject:** {draft.get('draft_subject', '')}

---

{draft.get('draft_body', '')}

---

## Actions
- **[✓ APPROVE & SEND](#approve-and-send)** — Send this email now
- **[✎ EDIT DRAFT](#edit-draft)** — Modify the content before sending
- **[✗ DISCARD](#discard)** — Skip this email

---

## Status
- Status: **PENDING APPROVAL**
- Draft ID: `{draft.get('email_id', 'N/A')}`
- Template Used: `{draft.get('template_used', 'general')}`

> 💡 **Tip:** Edit the markdown directly to customize your response, then use the approval commands.
"""
        
        draft_file.write_text(markdown_content)
        return str(draft_file)
    
    def create_approval_request(self, draft: Dict) -> Dict:
        """
        Create an approval request object for VS Code Webview
        """
        request_id = draft.get('email_id', '')
        
        approval_request = {
            'id': request_id,
            'timestamp': datetime.now().isoformat(),
            'from': draft.get('original_sender', ''),
            'originalSubject': draft.get('original_subject', ''),
            'draftSubject': draft.get('draft_subject', ''),
            'draftBody': draft.get('draft_body', ''),
            'status': 'pending',
            'actions': {
                'approve': True,
                'edit': True,
                'discard': True
            }
        }
        
        self.pending_approvals[request_id] = approval_request
        return approval_request
    
    def create_webview_html(self, drafts: List[Dict]) -> str:
        """
        Create HTML content for VS Code Webview
        Displays all pending drafts with approval controls
        """
        drafts_html = ""
        for idx, draft in enumerate(drafts, 1):
            drafts_html += f"""
            <div class="draft-card" data-draft-id="{draft.get('email_id', '')}">
                <h3>Draft {idx}</h3>
                <div class="email-info">
                    <p><strong>From:</strong> {draft.get('original_sender', '')}</p>
                    <p><strong>Original Subject:</strong> {draft.get('original_subject', '')}</p>
                </div>
                
                <div class="draft-content">
                    <h4>Your Response:</h4>
                    <p><strong>To:</strong> {draft.get('original_sender', '')}</p>
                    <p><strong>Subject:</strong> {draft.get('draft_subject', '')}</p>
                    <pre>{draft.get('draft_body', '')}</pre>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-success" onclick="approve('{draft.get('email_id', '')}')">
                        ✓ Approve & Send
                    </button>
                    <button class="btn btn-info" onclick="edit('{draft.get('email_id', '')}')">
                        ✎ Edit Draft
                    </button>
                    <button class="btn btn-danger" onclick="discard('{draft.get('email_id', '')}')">
                        ✗ Discard
                    </button>
                </div>
            </div>
            """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Email Drafts for Approval</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 20px;
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }}
        
        h1 {{
            margin-top: 0;
            border-bottom: 2px solid var(--vscode-focusBorder);
            padding-bottom: 10px;
        }}
        
        .draft-card {{
            background-color: var(--vscode-editorGroupHeader-tabsBackground);
            border: 1px solid var(--vscode-editorBorder);
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .email-info {{
            background-color: var(--vscode-editor-background);
            padding: 10px;
            border-radius: 3px;
            margin: 10px 0;
        }}
        
        .draft-content {{
            background-color: var(--vscode-editor-background);
            padding: 15px;
            border-radius: 3px;
            margin: 10px 0;
        }}
        
        pre {{
            overflow-x: auto;
            background-color: var(--vscode-editorBracketMatch-border);
            padding: 10px;
            border-radius: 3px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .action-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            opacity: 0.8;
            transform: translateY(-1px);
        }}
        
        .btn-success {{
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }}
        
        .btn-info {{
            background-color: var(--vscode-editorInfo-border);
            color: var(--vscode-editor-foreground);
        }}
        
        .btn-danger {{
            background-color: var(--vscode-editorError-border);
            color: var(--vscode-editor-foreground);
        }}
        
        .status {{
            margin-top: 10px;
            padding: 10px;
            border-radius: 3px;
            background-color: var(--vscode-editorWarning-background);
            color: var(--vscode-editorWarning-foreground);
        }}
    </style>
</head>
<body>
    <h1>📨 Email Drafts - Manual Approval Required</h1>
    <p>Review and approve email drafts before sending. no automatic sending is performed.</p>
    
    {drafts_html}
    
    <div class="status">
        <p><strong>Total Drafts:</strong> {len(drafts)}</p>
        <p>All drafts require manual approval before sending.</p>
    </div>
    
    <script>
        function approve(draftId) {{
            vscode.postMessage({{
                command: 'approve',
                draftId: draftId
            }});
        }}
        
        function edit(draftId) {{
            vscode.postMessage({{
                command: 'edit',
                draftId: draftId
            }});
        }}
        
        function discard(draftId) {{
            vscode.postMessage({{
                command: 'discard',
                draftId: draftId
            }});
        }}
        
        // VS Code Webview API (will be injected by extension)
        const vscode = acquireVsCodeApi ? acquireVsCodeApi() : {{}};
    </script>
</body>
</html>
"""
        return html_content
    
    def save_draft_json(self, drafts: List[Dict]) -> str:
        """Save drafts as JSON for programmatic access"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.draft_output_path / f"drafts_{timestamp}.json"
        
        json_file.write_text(json.dumps(drafts, indent=2))
        return str(json_file)
    
    def get_approval_status(self, draft_id: str) -> Optional[Dict]:
        """Get approval status of a draft"""
        return self.pending_approvals.get(draft_id)
    
    def mark_approved(self, draft_id: str):
        """Mark a draft as approved"""
        if draft_id in self.pending_approvals:
            self.pending_approvals[draft_id]['status'] = 'approved'
    
    def mark_rejected(self, draft_id: str):
        """Mark a draft as rejected"""
        if draft_id in self.pending_approvals:
            self.pending_approvals[draft_id]['status'] = 'rejected'
