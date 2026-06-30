# Security Architecture & Guardrails (SECURITY.md)

`research-pilot` implements a defense-in-depth security model to guard against prompt injections, adversarial overrides, and model hallucinations.

---

## 🛡️ Key Security Features

### 1. Active Input Sanitizer (`app/tools/sanitizer.py`)
To prevent **Indirect Prompt Injections** from untrusted web text scraped during literature aggregation, the system intercepts scraped content:
* **Regex Filtering**: A pre-indexing sanitation check scans text line-by-line for common override patterns (e.g. *"ignore previous instructions"*, *"system override"*, *"jailbreak"*, *"forget everything"*).
* **Isolation and Stripping**: Any line containing an adversarial signature is flagged and stripped out before it is chunked, embedded, or written to the database.

### 2. Output Guardrails & Citation Validator (`ReportAgent._validate_citations`)
To prevent **Hallucinations** and secure information integrity:
* **Programmatic Verification**: Every source link (markdown format `[title](url)`) in the final generated Markdown report is programmatically cross-referenced against the raw index corpus stored inside the local FAISS database.
* **Redaction**: If the model invents/hallucinates a source URL not present in the indexed literature, the citation is stripped and replaced with `[Hallucination Blocked: Source URL not found in references]`.

### 3. Model Context Protocol (MCP) Process Isolation
* The FAISS database is encapsulated within the `Research-Pilot-Vault` FastMCP server.
* The orchestrator and agents communicate with the database via standard input/output (stdio) channels using tool executions, preventing direct model manipulation of the vector files.

### 4. Secret Prevention & Commit Hook
* No API keys or credentials are ever hardcoded in the repository. Environment variables are loaded dynamically from a git-ignored `.env` file.
* A pre-commit hook runs on Git stages to verify no raw string API keys (`AIzaSy...` style Gemini/Google Cloud keys) are accidentally committed to source control.
