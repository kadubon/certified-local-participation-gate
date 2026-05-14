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
    task=TaskSnapshot(task_id="demo"),
    agent=AgentSnapshot(agent_id="agent.local", capabilities=["act"]),
    authority=AuthoritySnapshot(actor="agent.local"),
    evidence=EvidenceSnapshot(),
    uncertainty=UncertaintyEnvelope(),
    attribution=AttributionState(),
    budget=CostBudget(budget_remaining=10),
    policy=demo_policy(),
)

print(receipt.decision.value)
print(receipt.receipt_digest)
