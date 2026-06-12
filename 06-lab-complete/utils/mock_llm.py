"""Mock LLM used by the final lab project so it runs without paid API keys."""
import random
import time


MOCK_RESPONSES = {
    "default": [
        "This is a mock AI response. In production, replace it with OpenAI or Anthropic.",
        "The agent is running correctly. Ask another deployment question.",
        "Your question was received by the cloud-ready AI agent.",
    ],
    "docker": [
        "Docker packages the app and its runtime so the same image can run locally or in cloud."
    ],
    "deploy": [
        "Deployment means moving code from a local machine to a hosted service with config, health checks, and logs."
    ],
    "health": [
        "The health endpoint lets the platform confirm that the container process is alive."
    ],
}


def ask(question: str, delay: float = 0.05) -> str:
    """Return a deterministic-enough mock answer without calling an external LLM."""
    time.sleep(delay + random.uniform(0, 0.03))
    question_lower = question.lower()
    for keyword, responses in MOCK_RESPONSES.items():
        if keyword in question_lower:
            return random.choice(responses)
    return random.choice(MOCK_RESPONSES["default"])
