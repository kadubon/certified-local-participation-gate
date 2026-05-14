from clpg_test_helpers import DIGEST, full_inputs
from hypothesis import given
from hypothesis import strategies as st

from clpg import (
    ParticipationDecision,
    ParticipationPolicy,
    TaskSnapshot,
    UncertaintyEnvelope,
    canonical_json,
    decide_participation,
    sha256_digest,
)


@given(st.dictionaries(st.text(min_size=1), st.integers(), max_size=8))
def test_canonicalization_idempotent(payload: dict[str, int]) -> None:
    assert canonical_json(payload) == canonical_json(payload)


@given(st.text(min_size=1), st.text(min_size=1))
def test_task_digest_mutation_changes_when_ids_differ(a: str, b: str) -> None:
    if a != b:
        assert sha256_digest(TaskSnapshot(task_id=a)) != sha256_digest(TaskSnapshot(task_id=b))


@given(st.floats(min_value=0.0, max_value=1.0), st.floats(min_value=0.0, max_value=1.0))
def test_tighter_harm_threshold_does_not_create_act(harm: float, threshold: float) -> None:
    strict_receipt = decide_participation(
        task=full_inputs()["task"],  # type: ignore[arg-type]
        agent=full_inputs()["agent"],  # type: ignore[arg-type]
        authority=full_inputs()["authority"],  # type: ignore[arg-type]
        evidence=full_inputs()["evidence"],  # type: ignore[arg-type]
        uncertainty=UncertaintyEnvelope(
            harm_upper_bound=harm,
            service_faults={"fault_profile_digest": DIGEST},
        ),
        attribution=full_inputs()["attribution"],  # type: ignore[arg-type]
        budget=full_inputs()["budget"],  # type: ignore[arg-type]
        policy=ParticipationPolicy(max_harm_upper_bound=threshold / 2),
    )
    weak_receipt = decide_participation(
        task=full_inputs()["task"],  # type: ignore[arg-type]
        agent=full_inputs()["agent"],  # type: ignore[arg-type]
        authority=full_inputs()["authority"],  # type: ignore[arg-type]
        evidence=full_inputs()["evidence"],  # type: ignore[arg-type]
        uncertainty=UncertaintyEnvelope(
            harm_upper_bound=harm,
            service_faults={"fault_profile_digest": DIGEST},
        ),
        attribution=full_inputs()["attribution"],  # type: ignore[arg-type]
        budget=full_inputs()["budget"],  # type: ignore[arg-type]
        policy=ParticipationPolicy(max_harm_upper_bound=threshold),
    )
    if weak_receipt.decision != ParticipationDecision.ACT:
        assert strict_receipt.decision != ParticipationDecision.ACT
