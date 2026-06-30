---
name: research-indexer
description: Use this skill whenever an agent needs to chunk textual research documents, write them to the local FAISS index, or retrieve contextual segments via the Research-Pilot-Vault server.
---

# Research Indexer Skill

This skill provides helper scripts to interact with the local `Research-Pilot-Vault` FastMCP server. It enables chunking raw literature text and writing it to the local FAISS database, as well as querying the database for context matches.

## Scripts Included
1. [build_index.py](file:///C:/Users/aatka/research-pilot/.agents/skills/research-indexer/scripts/build_index.py): Chunks a text file and registers it in the FAISS vector database.
2. [query_index.py](file:///C:/Users/aatka/research-pilot/.agents/skills/research-indexer/scripts/query_index.py): Queries the FAISS vector database for relevant matching clips.

## Execution via Command Line

To index a raw findings document:
```bash
python .agents/skills/research-indexer/scripts/build_index.py --file <path_to_txt> --url <citation_url>
```

To query the local vector index:
```bash
python .agents/skills/research-indexer/scripts/query_index.py --query "<your_query>"
```
