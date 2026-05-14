from clpg import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    ClaimSnapshot,
    CostBudget,
    EvidenceSnapshot,
    ParticipationPolicy,
    TaskSnapshot,
    UncertaintyEnvelope,
    decide_participation,
)

receipt = decide_participation(
    task=TaskSnapshot(
        task_id="authority-demo",
        protected_action=True,
        requested_action="write_file",
        claim=ClaimSnapshot(
            requested_action="write_file",
            protected_action=True,
        ),
    ),
    agent=AgentSnapshot(agent_id="agent.local", capabilities=["write_file"]),
    authority=AuthoritySnapshot(actor="agent.local"),
    evidence=EvidenceSnapshot(),
    uncertainty=UncertaintyEnvelope(),
    attribution=AttributionState(),
    budget=CostBudget(budget_remaining=10),
    policy=ParticipationPolicy(),
)

print(receipt.decision.value)
print([code.value for code in receipt.reason_codes])
