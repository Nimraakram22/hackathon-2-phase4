"""
Relevance guardrail agent for input validation.

This module implements input guardrails to validate task-related messages.
"""

from pydantic import BaseModel
from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrail, input_guardrail, RunContextWrapper, OpenAIChatCompletionsModel

from .gemini_client import gemini_client


class RelevanceCheck(BaseModel):
    """
    Relevance check result from guardrail agent.

    Attributes:
        is_task_related: Whether the input is related to task management
        reason: Explanation for the relevance decision
    """

    is_task_related: bool
    reason: str


# Relevance checker agent
relevance_agent = Agent(
    name="Relevance Checker",
    instructions=(
        "Check if the user's input is related to task management. "
        "Task management includes: creating tasks, viewing tasks, updating tasks, "
        "deleting tasks, completing tasks, and asking about tasks. "
        "Return is_task_related=True if the input is about any of these operations. "
        "Return is_task_related=False if the input is unrelated (e.g., general chat, "
        "off-topic questions, spam). Provide a brief reason for your decision."
    ),
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client,
    ),
    output_type=RelevanceCheck,
)


@input_guardrail(run_in_parallel=False)
async def validate_input_relevance(
    ctx: RunContextWrapper, agent: Agent, input: str
) -> GuardrailFunctionOutput:
    """
    Validate that user input is task-related before processing.

    Args:
        ctx: Run context wrapper
        agent: Agent being guarded
        input: User input string

    Returns:
        GuardrailFunctionOutput with tripwire_triggered=True if input is not task-related
    """
    result = await Runner.run(relevance_agent, input, context=ctx.context)

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_task_related,
    )


# Blocking guardrail that prevents execution if input is not task-related
blocking_guardrail = validate_input_relevance
