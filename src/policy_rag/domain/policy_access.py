from policy_rag.domain.access import PolicyAccessContext
from policy_rag.domain.policy import PolicyDocument


def can_retrieve_policy(
    policy: PolicyDocument,
    context: PolicyAccessContext,
) -> bool:
    """Return whether a policy is effective and accessible for the request."""

    return policy.is_effective_on(context.as_of) and policy.is_accessible_to(context.user_groups)
