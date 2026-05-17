# AgentX-AgentBeats Sprint 4: Lambda Agent Security Custom Track

**Agent:** `purple-pi-bench`
**Image:** `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest`
**Track:** Lambda Agent Security (Custom Track), Sprint 4
**Deadline:** 2026-05-24
**Author:** Mukunda Katta

## What this agent does

`purple-pi-bench` is an A2A-compatible purple agent. It takes a user message plus a policy block from the green grader, picks one of four actions (`respond`, `refuse`, `escalate`, `request_info`), and emits a single JSON object with `action`, `arguments`, and `reasoning`. The grader scores that JSON against the policy.

It is small on purpose. The whole policy logic is one system prompt plus a strict JSON parser. Provider calls go through `litellm`, so the same image runs on OpenAI, Anthropic, Gemini, or any OpenRouter model by changing one env var.

## How each Pi-Bench dimension is targeted

Pi-Bench scores nine dimensions. Each one shows up in a specific design choice:

| Dimension | Design choice |
|---|---|
| **Compliance** | System prompt lists compliance first and tells the model to quote rules, not paraphrase them. JSON-only output means the grader can match rule text directly. |
| **Understanding** | The prompt tells the model to read the user request literally before generalizing. Temperature is pinned to 0 so the same input yields the same parse. |
| **Robustness** | The prompt declares that no user message can override the principles. Provider errors fall back to a structured refuse, never a free-text best guess. |
| **Process** | Principles are numbered. The model follows the order, top to bottom. Step skipping is called out as a fail. |
| **Restraint** | `request_info` is a first-class action. If the request is ambiguous and a refuse would block legit work, the agent asks instead of guessing. |
| **Conflict Resolution** | The prompt names the tie-breakers: safety beats convenience, privacy beats speed. The model has to pick one rule and cite which one it dropped. |
| **Detection** | `refuse` requires quoting the violated rule in `reasoning`. No quoted rule, no refuse. |
| **Explainability** | `reasoning` is a required field on every output. It is graded and never empty. |
| **Adaptation** | The prompt tells the model to apply policy changes that the user message triggers, not the prior turn's policy. Conversation state is preserved per `context_id`. |

The agent class keeps the full message history per A2A `context_id`, so multi-turn scenarios (a policy that changes mid-conversation) stay coherent.

## Why this design

Three bets:

1. **Structured output is more graded than prose.** A grader can score JSON. Free text needs an LLM judge, and judges drift.
2. **A short prompt is more debuggable than a long one.** Nine numbered principles fit on one screen. When a Pi-Bench score is low, the failing dimension maps to a single line.
3. **Restraint is cheap.** Refusing with a real reason is almost always better than confabulating. The agent leans on `request_info` and `refuse` when the rule is unclear.

## How to register on agentbeats.dev

1. Open https://agentbeats.dev/ and sign in with GitHub.
2. Click **Register Agent**.
3. Choose **Purple** as the agent role.
4. Fill in:
   - Display name: `purple-pi-bench`
   - Docker image: `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest`
   - Category: `Agent Safety` (add Tau-Bench, OfficeQA, BrowseComp+, SWE-bench Pro if you plan to run there too)
   - Description: copy the top of the README
5. Save. Copy the agent ID from the agent page.

## How to Quick Submit against Pi-Bench

1. From agentbeats.dev, open the Pi-Bench green agent page.
2. Click **Quick Submit**.
3. Pick `purple-pi-bench` as the participant.
4. Paste an `OPENAI_API_KEY` (or the matching key for whichever provider you set in `PURPLE_LLM`).
5. Submit. The platform runs a GitHub Action that boots both agents, runs the scenarios, and posts results back as a PR. Once the green-agent maintainer merges, the score lands on the leaderboard.

## Sprint 4 eligibility

To qualify for judging, the same image must be evaluated against **at least 5 green agents across at least 3 distinct categories**. The plan:

1. Pi-Bench (Agent Safety): primary target.
2. Tau-Bench (Tool Use).
3. OfficeQA (Productivity).
4. BrowseComp+ (Web).
5. SWE-bench Pro (Coding).

Same image, same prompt, different green graders. If a category needs domain knowledge the policy-compliance prompt can't carry, that's signal for a follow-up sprint.

## Reproducing the result

```bash
docker run --rm -p 9020:9020 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest
```

Card at `http://localhost:9020/`. The `scripts/local_test.sh` helper boots the server and curls a sample message at it.

Tests: `pytest tests/` (no API keys needed; the smoke test mocks `litellm.completion`).

## Repo

https://github.com/MukundaKatta/agentbeats-purple-pi-bench
