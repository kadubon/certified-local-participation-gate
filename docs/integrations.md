# Integrations

No integrations are implemented in v0.1.1.

Future adapters may map:

- CMGL receipts into evidence inputs;
- no-meta-authority-runtime receipts into authority inputs;
- OASG ledgers into workflow promotion or quarantine evidence;
- CWC reports into bottleneck analysis;
- OAWM and MemoryFlow records into replayability and evidence state;
- LangGraph and CrewAI hooks into pre-execution calls to `decide_participation`.

Adapters must not treat natural language or external records as authority merely because they are present.
