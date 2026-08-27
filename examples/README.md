# Consumer fixtures

These files are wire-contract examples. They demonstrate portability across independent L9 concerns and
create no imports or runtime dependencies on Cog, Ops, Goose, Program Execution, Deploy, or model runtimes.

| Fixture | Canonical family | Illustrative producer only |
|---|---|---|
| `cog-compile-span.json` | `execution_span` | Cognitive Runtime |
| `ops-context-span.json` | `execution_span` | L9 Ops / context plane |
| `goose-tool-call.json` | `tool_call` | Goose/execution runtime |
| `pe-attempt.json` | `attempt` | Program Execution |
| `deploy-outcome.json` | `outcome` | Deployment |
| `example-validation-event.json` | `validation` | Generic validator |
| `example-failure-event.json` | `failure` | Generic producer |
| `example-usage-event.json` | `usage` | Model/provider runtime |

Together the fixture corpus covers all seven first-class event families. Fixture presence proves schema/model
portability only. It is **not runtime-adoption evidence** for any named producer. See
`docs/ADOPTION_CONTRACT.md`.
