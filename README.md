# agentbeats-purple-pi-bench

An A2A-compatible purple agent for the AgentBeats platform, built for the **AgentX-AgentBeats Phase 2 Sprint 4 Lambda Agent Security Custom Track** (deadline 2026-05-24).

The agent is designed for policy-compliance benchmarks like **Pi-Bench**, which scores agents across nine dimensions: Compliance, Understanding, Robustness, Process, Restraint, Conflict Resolution, Detection, Explainability, and Adaptation.

## Design

The agent's system prompt mirrors the nine Pi-Bench dimensions in priority order. Every output is a single JSON object with `action` / `arguments` / `reasoning` — the `reasoning` field directly targets the Explainability dimension and gives the green-agent grader something concrete to score.

Defensive defaults favor Restraint over hallucination: when the model errors or returns malformed output, the agent emits a structured refusal rather than a free-text best-effort.

## Run locally

```bash
uv sync
uv run src/server.py --host 0.0.0.0 --port 9020 --llm openai/gpt-4o-mini
```

Set provider credentials via env: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, or any litellm-compatible config.

The agent card is served at `http://localhost:9020/`.

## Build the container

A GitHub Actions workflow builds and pushes to `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest` on every push to main.

Manual build:

```bash
docker build -t purple-pi-bench .
docker run --rm -p 9020:9020 -e OPENAI_API_KEY=$OPENAI_API_KEY purple-pi-bench
```

## Register on AgentBeats

1. Sign in to https://agentbeats.dev/ (GitHub OAuth).
2. Click **Register Agent**, choose **Purple**.
3. Fill in:
   - Display name: `purple-pi-bench`
   - Docker image: `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest`
   - Category: `Agent Safety` (plus any others where you intend to run Quick Submits)
4. Copy the agent ID from your registered agent's page.

## Run a first Quick Submit against Pi-Bench

1. Open the Pi-Bench green agent on agentbeats.dev.
2. Click **Quick Submit**.
3. Select `purple-pi-bench` as the participant.
4. Add your `OPENAI_API_KEY` (or whichever provider you set in `PURPLE_LLM`).
5. Submit. The GitHub Action runs the assessment, posts results, the green-agent author merges the PR, your score lands on the leaderboard.

## Eligibility note

To be eligible for **Sprint 4 judging**, the same purple agent must be evaluated against **≥5 green agents across ≥3 distinct categories**. Once the Pi-Bench run passes, repeat the Quick Submit flow against four more green agents (Tau-Bench, OfficeQA, BrowseComp+, SWE-bench Pro are good adjacent picks).

## License

Apache 2.0.
