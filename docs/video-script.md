# 90-second demo video script

Target: a screen-capture walkthrough of `purple-pi-bench` from container to leaderboard score. Aim for under 90 seconds total. Voiceover lines are written to read out loud at a normal pace.

## Setup before recording

- Tabs ready in this order: GHCR package page, agentbeats.dev/register, Pi-Bench Quick Submit, leaderboard.
- Terminal in a clean directory with the GHCR image already pulled.
- Mic check. No background music.

## Shot list

### 0:00 to 0:10: Opening (GHCR image)

**Screen:** GHCR page for `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest`. Zoom on the pull command.

**Voiceover:**
> This is `purple-pi-bench`. It's a policy-compliance agent for AgentBeats. One Docker image, runs anywhere, scores itself on the Pi-Bench leaderboard.

### 0:10 to 0:30: Live `docker run`

**Screen:** Terminal. Run:
```
docker run --rm -p 9020:9020 -e OPENAI_API_KEY=$OPENAI_API_KEY ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest
```
Then in a second pane: `curl http://localhost:9020/.well-known/agent.json | jq`.

**Voiceover:**
> One command boots the A2A server on port nine-oh-two-zero. The agent card is live. The container is the same one I'll register on agentbeats.dev.

### 0:30 to 0:50: Registration form

**Screen:** agentbeats.dev registration form, filled in:
- Display name: `purple-pi-bench`
- Docker image: `ghcr.io/MukundaKatta/agentbeats-purple-pi-bench:latest`
- Role: Purple
- Category: Agent Safety

Hover over the Save button.

**Voiceover:**
> Register on agentbeats.dev. Paste the image, pick the role, set the category. Save. That's it for setup.

### 0:50 to 1:10: Quick Submit

**Screen:** Pi-Bench green agent page. Click **Quick Submit**. Pick `purple-pi-bench`. Paste API key. Click submit. Cut to the GitHub Action page showing the run kicking off.

**Voiceover:**
> Quick Submit runs the eval. Pi-Bench grades nine dimensions: compliance, understanding, robustness, process, restraint, conflict resolution, detection, explainability, adaptation. A GitHub Action runs the match and posts a PR.

### 1:10 to 1:30: Leaderboard result

**Screen:** Leaderboard with `purple-pi-bench` row highlighted. Show the dimension breakdown if visible. End on the repo URL overlaid.

**Voiceover:**
> Result lands on the leaderboard. Source, Dockerfile, tests, and submission writeup are in the repo. Sprint 4 entry. Done.

## Notes

- Keep cursor movement minimal. Cut between shots rather than zooming.
- Don't read JSON aloud. Show it on screen and keep talking.
- If the GitHub Action takes more than ten seconds to show progress, edit it down. Don't sit on a spinner.
- Export at 1080p. Mono audio is fine.
