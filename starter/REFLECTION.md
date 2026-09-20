# Reflection

For the `MemoryHook` implementation, I chose to store `actor_id` and `session_id` as
instance attributes set in `__init__`, rather than pulling them from `agent.state` as
shown in a similar course demo. This kept the hook self-contained and matched the
starter code's own docstring guidance, making the retrieval and save logic easier to
reason about independently of how the agent object was constructed elsewhere in the
entrypoint. For `get_namespaces`, I added a fallback that checks both
`namespaceTemplates` and the legacy `namespaces` field, since AgentCore's API has used
both keys across versions — a small defensive choice that avoided a brittle dependency
on one specific API version.

The most significant challenge I encountered was a Windows-specific bug in the
`agentcore` CLI's argument handling: any multi-word value in the JSON payload (e.g.
`"Can you track order ORD-001"`) caused the CLI to silently split the string into
multiple invalid arguments, regardless of quoting style (single quotes, backslash
escapes, PowerShell's native doubled-quote escaping, or the `--%` stop-parsing token).
After ruling out five quoting techniques and a full `uv` toolchain upgrade, I traced
the deeper issue to a second bug: deployment packages built on Windows lost the Unix
executable permission bit on Playwright's bundled Node.js driver, causing the browser
tool to fail with `PermissionError: [Errno 13]` once deployed. I resolved both issues
by installing WSL2 and rebuilding the deployment package inside a native Ubuntu
environment, which correctly preserved file permissions and also resolved the CLI
argument bug (bash handles quoted strings natively). This traced a Windows-Linux
compatibility issue several layers deep — from a CLI symptom to a filesystem
permissions root cause — rather than settling for a workaround at the surface level.

For a production version of this agent, I would replace the Gateway's `NONE`
authorizer with an AgentCore Identity-backed credential, since the current setup
allows unauthenticated invocation of the `order-tracker` and `refund-processor`
tools. I would also add `aws-opentelemetry-distro` for request tracing, since the
Browser and Code Interpreter tools have highly variable latency that would benefit
from per-invocation observability in a real deployment.
