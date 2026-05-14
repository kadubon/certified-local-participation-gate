from clpg import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    CostBudget,
    EvidenceSnapshot,
    TaskSnapshot,
    UncertaintyEnvelope,
    decide_participation,
)
from clpg.policy import demo_policy

receipt = decide_participation(
    task=TaskSnapshot(task_id="verify-demo"),
    agent=AgentSnapshot(agent_id="agent.local", capabilities=["act"], verification_capability=True),
    authority=AuthoritySnapshot(actor="agent.local"),
    evidence=EvidenceSnapshot(required_evidence=["source-record"], verification_available=True),
    uncertainty=UncertaintyEnvelope(),
    attribution=AttributionState(),
    budget=CostBudget(budget_remaining=10, verification_cost_upper_bound=1),
    policy=demo_policy(),
)

print(receipt.decision.value)
print([code.value for code in receipt.reason_codes])
