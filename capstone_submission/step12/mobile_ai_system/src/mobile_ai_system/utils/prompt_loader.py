from pathlib import Path


PROMPT_ROOT = (
    Path(__file__).resolve().parent.parent
    / "prompts"
)


def load_agent_prompts(
    agent_name: str,
) -> str:
    """
    Load all markdown prompts belonging to one agent.

    Example:

        load_agent_prompts("report")

    Every *.md file is concatenated in filename order.
    """

    folder = PROMPT_ROOT / agent_name

    if not folder.exists():
        raise FileNotFoundError(
            f"Prompt folder does not exist: {folder}"
        )

    prompt_sections = []

    for file in sorted(folder.glob("*.md")):

        prompt_sections.append(
            file.read_text(
                encoding="utf-8"
            ).strip()
        )

    return "\n\n".join(prompt_sections)