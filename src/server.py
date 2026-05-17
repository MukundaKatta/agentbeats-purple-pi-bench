import argparse
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from executor import Executor


def main():
    parser = argparse.ArgumentParser(description="Run the policy-compliant purple agent.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9020)
    parser.add_argument("--card-url", default=None)
    parser.add_argument("--llm", default=os.getenv("PURPLE_LLM", "openai/gpt-4o-mini"))
    args = parser.parse_args()

    os.environ.setdefault("PURPLE_LLM", args.llm)

    skill = AgentSkill(
        id="policy_compliance",
        name="Policy Compliance",
        description=(
            "Acts on user requests while strictly following provided policies. "
            "Designed for Pi-Bench-style evaluations across the nine policy "
            "compliance dimensions."
        ),
        tags=["benchmark", "agent-safety", "policy-compliance", "pi-bench"],
        examples=[],
    )

    card = AgentCard(
        name="purple_pi_bench",
        description="Policy-compliant purple agent for AgentBeats / Pi-Bench.",
        url=args.card_url or f"http://{args.host}:{args.port}/",
        version="0.1.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    handler = DefaultRequestHandler(
        agent_executor=Executor(),
        task_store=InMemoryTaskStore(),
    )

    app = A2AStarletteApplication(agent_card=card, http_handler=handler)

    uvicorn.run(
        app.build(),
        host=args.host,
        port=args.port,
        timeout_keep_alive=300,
    )


if __name__ == "__main__":
    main()
