from dataclasses import dataclass
from datetime import datetime

from permit import Permit
from pydantic_ai import RunContext


def get_current_time() -> str:
    return datetime.now()


@dataclass
class AgentContext:
    recentquery: str
    usermetadata: dict
    action: str
    resource: str
    permit: Permit


# Prompt Filtering: is the prompt length too long? or does it contain any SQL injection?
# or is the user active?
async def check_prompt_filtering(ctx: RunContext[AgentContext]) -> bool:
    """
    Check if the prompt is too long or contains SQL injection or if the user is active.

    Args:
        ctx (RunContext[AgentContext]): The context of the agent.
        prompt (str): The prompt to check.

    Returns:
        bool: True if the prompt is valid, False otherwise.
    """
    prompt = ctx.deps.recentquery
    if len(prompt) > 1000:
        return False
    if prompt.lower() in ["drop", "delete", "alter"]:
        return False
    if not ctx.deps.usermetadata.get("is_active"):
        return False
    return True


# RAG Data Protection: Prevent employees from accessing hr data or financial data
# employee can only access the customer data, managers can access the customer data and hr data
async def check_user_permission(ctx: RunContext[AgentContext]) -> bool:
    """
    Check if the user has permission to access the resource.

    Args:
        ctx (RunContext[AgentContext]): The context of the agent.

    Returns:
        bool: True if the user has permission, False otherwise.
    """
    print(ctx.deps.usermetadata.get("id"), ctx.deps.action, ctx.deps.resource)
    permitted = await ctx.deps.permit.check(
        user=str(ctx.deps.usermetadata.get("id")),
        action=ctx.deps.action,
        resource=ctx.deps.resource,
    )
    if not permitted:
        return False
    return True

