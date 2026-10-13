# AI Customer Support Agent — Amazon Bedrock AgentCore + Strands SDK

A customer support AI agent for an e-commerce platform, built with **Amazon Bedrock
AgentCore** and the **Strands SDK**. The agent tracks orders, processes refunds, answers
product and policy questions with RAG, calculates loyalty discounts, browses live web
pages, and remembers customers across separate sessions.

> **Status:** Completed and passed the Udacity project review. All 6 required test
> scenarios were run against the deployed agent (screenshots in `starter/test_results/`).
> The agent runtimes and the Knowledge Base were deleted afterward to stop AWS charges,
> so `test_agent.py` points at an agent that no longer exists.

## What it does

- **Tracks orders and processes refunds** through an AgentCore Gateway that exposes a
  REST API (API Gateway + Lambda) and a Lambda function as MCP tools
- **Answers product and policy questions** with Retrieval-Augmented Generation against a
  Bedrock Knowledge Base backed by an S3 document store
- **Remembers customers across sessions** with AgentCore Memory (semantic-fact and
  user-preference strategies)
- **Calculates loyalty discounts** with the AgentCore Code Interpreter, so the arithmetic
  runs as code in a sandbox instead of being estimated by the model
- **Browses live web pages** with the AgentCore Browser tool

## Architecture

```
main.py (Strands Agent + BedrockAgentCoreApp, deployed to AgentCore Runtime)
  ├── search_knowledge_base      → Bedrock Knowledge Base (RAG)
  ├── calculate_loyalty_discount → AgentCore Code Interpreter
  ├── AgentCoreBrowser           → AgentCore Browser tool
  ├── MemoryHook                 → AgentCore Memory (cross-session recall)
  └── Gateway tools (via MCPClient)
        ├── order-tracker        → API Gateway → Lambda
        └── refund-processor     → Lambda (direct invoke)
```

Model: `global.amazon.nova-2-lite-v1:0` via Amazon Bedrock. Region: `us-east-1`.

## Project structure

```
starter/
├── main.py                  — agent implementation (all 8 TODOs completed)
├── lambda/
│   ├── order_tracker.py     — order/customer lookup Lambda (Udacity starter)
│   ├── refund_processor.py  — refund tools Lambda (Udacity starter)
│   └── lambda_schema        — tool schema for the refund-processor Gateway target
├── product_catalog.txt      — knowledge base source data (Udacity starter)
├── requirements.txt         — Linux-targeted dependencies for Direct Code Deploy
├── test_agent.py            — boto3 helper used for early testing (see Testing)
├── test_results/            — screenshots of the 6 required test scenarios
└── REFLECTION.md            — written reflection on design decisions and challenges
```

## Testing

All 6 required scenarios were run against the deployed agent with the AgentCore CLI:

```bash
agentcore invoke '{"prompt": "...", "customer_id": "CUST-123", "session_id": "..."}'
```

1. Order tracking (Gateway → `order-tracker`)
2. Refund processing (Gateway → `refund-processor`)
3. Knowledge Base question (RAG)
4. Long-term memory across two sessions
5. Loyalty discount (Code Interpreter)
6. Browser tool

Notes:
- Memory extraction runs asynchronously, so the second session in the memory test only
  recalled the first session's facts after waiting roughly 90 seconds.
- `test_agent.py` is a boto3 script I used early on while the CLI was failing on
  Windows. The final screenshots come from `agentcore invoke`. The ARN in the script is
  for a deleted agent.

## Deployment notes

Deployed with AgentCore Direct Code Deploy (no Docker) from a WSL2 Ubuntu environment.
Building and invoking from Windows PowerShell caused a CLI argument-quoting problem and a
`PermissionError` on Playwright's bundled Node driver once deployed. Building on native
Linux avoided both. The permission error is most likely a lost executable bit from
zipping on Windows; I did not prove that. See `REFLECTION.md` for the debugging story.

## How this was built, and attributions

This project was completed for Udacity's "Future AWS Agent Engineer" Nanodegree
(AWS AI & ML Scholars program).

**Starter material from Udacity:** the `main.py` scaffolding and docstrings, both Lambda
files, `lambda_schema`, and `product_catalog.txt` come from the course starter repo
(https://github.com/udacity/cd14763-project-starter) and are unmodified apart from the
`main.py` TODO sections and config values.

**AI assistance:** the code in the `main.py` TODO sections (`MemoryHook`,
`get_namespaces`, `search_knowledge_base`, `calculate_loyalty_discount`, and the `invoke`
entrypoint) and the first draft of `REFLECTION.md` were written with Claude (Anthropic)
acting as a mentor and drafting assistant. I set up and operated the AWS resources
(Lambdas, API Gateway, Gateway, Knowledge Base, Memory, IAM permissions), deployed the
agent, ran the tests, and debugged the deployment problems described above.

**Course material and documentation consulted:** lesson demos for `MCPClient`,
`code_session().invoke()`, `HookProvider`/`register_hooks`, the Knowledge Base retrieve
pattern, and `AgentCoreBrowser` (the demos use a fictional "WanderBot" travel scenario;
the patterns were adapted to customer support). AWS documentation for `bedrock-agentcore`
IAM actions and the `agentcore configure --disable-otel` flag. A public GitHub issue on
the `bedrock-agentcore-starter-toolkit` repo about an OpenTelemetry shebang bug.