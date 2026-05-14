from clpg_test_helpers import DIGEST, full_inputs, full_task, verification_portfolio

from clpg import (
    AgentSnapshot,
    AttributionState,
    AuthoritySnapshot,
    ClaimRole,
    ClaimSnapshot,
    ControllerCertificateSnapshot,
    CostBudget,
    EvidenceSnapshot,
    ParticipationDecision,
    ParticipationPolicy,
    ReasonCode,
    TaskSnapshot,
    UncertaintyEnvelope,
    decide_participation,
)


def base_inputs() -> dict[str, object]:
    return full_inputs()


def decide(**overrides: object):
    data = base_inputs()
    data.update(overrides)
    return decide_participation(**data)  # type: ignore[arg-type]


def test_act_when_all_strict_conditions_pass() -> None:
    receipt = decide()
    assert receipt.decision == ParticipationDecision.ACT
    assert receipt.reason_codes == [ReasonCode.ACT_CONDITIONS_SATISFIED]


def test_minimal_strict_input_does_not_act() -> None:
    receipt = decide_participation(
        task=TaskSnapshot(task_id="minimal"),
        agent=AgentSnapshot(agent_id="agent", capabilities=["act"]),
        authority=AuthoritySnapshot(actor="agent"),
        evidence=EvidenceSnapshot(),
        uncertainty=UncertaintyEnvelope(),
        attribution=AttributionState(),
        budget=CostBudget(budget_remaining=10),
        policy=ParticipationPolicy(),
    )
    assert receipt.decision != ParticipationDecision.ACT


def test_protected_action_without_authority_refuses() -> None:
    receipt = decide(
        task=TaskSnapshot(
            task_id="t1",
            requested_action="write_file",
            protected_action=True,
            claim=ClaimSnapshot(requested_action="write_file", protected_action=True),
        ),
        agent=AgentSnapshot(agent_id="agent", capabilities=["write_file"]),
        authority=AuthoritySnapshot(actor="agent"),
    )
    assert receipt.decision == ParticipationDecision.REFUSE
    assert ReasonCode.PROTECTED_ACTION_WITHOUT_AUTHORITY in receipt.reason_codes


def test_explicit_escalation_for_protected_action() -> None:
    receipt = decide(
        task=TaskSnapshot(
            task_id="t1",
            requested_action="write_file",
            protected_action=True,
            claim=ClaimSnapshot(requested_action="write_file", protected_action=True),
        ),
        agent=AgentSnapshot(agent_id="agent", capabilities=["write_file"]),
        authority=AuthoritySnapshot(actor="agent"),
        policy=ParticipationPolicy(allow_escalate=True, escalation_target="human-review"),
    )
    assert receipt.decision == ParticipationDecision.ESCALATE
    assert ReasonCode.ESCALATION_POLICY_SELECTED in receipt.reason_codes


def test_non_protected_action_outside_authority_refuses_in_strict_mode() -> None:
    receipt = decide(
        authority=AuthoritySnapshot(
            actor="agent",
            permitted_actions=["other"],
            valid=True,
            authority_digest=DIGEST,
        )
    )
    assert receipt.decision == ParticipationDecision.REFUSE
    assert ReasonCode.AUTHORITY_SCOPE_MISMATCH in receipt.reason_codes


def test_authority_actor_mismatch_refuses_in_strict_mode() -> None:
    receipt = decide(
        authority=AuthoritySnapshot(
            actor="other-agent",
            permitted_actions=["act"],
            valid=True,
            authority_digest=DIGEST,
        )
    )
    assert receipt.decision == ParticipationDecision.REFUSE
    assert ReasonCode.AUTHORITY_ACTOR_MISMATCH in receipt.reason_codes


def test_authority_certificate_missing_refuses_in_strict_mode() -> None:
    receipt = decide(
        authority=AuthoritySnapshot(
            actor="agent",
            permitted_actions=["act"],
            valid=True,
        )
    )
    assert receipt.decision == ParticipationDecision.REFUSE
    assert ReasonCode.AUTHORITY_CERTIFICATE_MISSING in receipt.reason_codes


def test_null_claim_withdraws() -> None:
    receipt = decide(task=full_task(role=ClaimRole.NONE))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.NULL_CLAIM_WITHDRAWN in receipt.reason_codes


def test_strict_claim_snapshot_missing_blocks_act() -> None:
    task = full_task().model_copy(update={"claim": None})
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CLAIM_SNAPSHOT_MISSING in receipt.reason_codes


def test_demo_policy_allows_legacy_task_fields_without_claim() -> None:
    task = TaskSnapshot(task_id="demo", requested_action="act")
    receipt = decide(
        task=task,
        authority=AuthoritySnapshot(actor="agent"),
        evidence=EvidenceSnapshot(),
        uncertainty=UncertaintyEnvelope(),
        policy=ParticipationPolicy(
            mode="demo",
            strict_authority=False,
            strict_evidence=False,
            require_claim_snapshot=False,
            require_replayability=False,
            require_public_coordination_state=False,
            require_audited_participation_interface=False,
            require_controller_certificate=False,
            require_explicit_service_expiry=False,
            require_service_certificate_digests=False,
            require_service_fault_certificate=False,
            allow_implicit_feasible_actions=True,
            min_capability_lower_bound_for_act=0,
            min_success_lower_bound_for_act=0,
        ),
    )
    assert receipt.decision == ParticipationDecision.ACT


def test_protected_task_flag_cannot_be_weakened_by_claim() -> None:
    receipt = decide(
        task=TaskSnapshot(
            task_id="t1",
            requested_action="write_file",
            protected_action=True,
            claim=ClaimSnapshot(requested_action="write_file", protected_action=False),
        ),
        agent=AgentSnapshot(agent_id="agent", capabilities=["write_file"]),
        authority=AuthoritySnapshot(
            actor="agent",
            permitted_actions=["write_file"],
            valid=True,
            authority_digest=DIGEST,
        ),
    )
    assert receipt.decision == ParticipationDecision.REFUSE
    assert ReasonCode.PROTECTED_FLAG_CONFLICT in receipt.reason_codes


def test_target_required_roles_need_target_refs() -> None:
    for role in (ClaimRole.ASSIST, ClaimRole.VERIFY, ClaimRole.CONTINUE):
        task = full_task(role=role).model_copy(
            update={"claim": ClaimSnapshot(requested_role=role, requested_action="act")}
        )
        receipt = decide(task=task)
        assert receipt.decision == ParticipationDecision.WITHDRAW
        assert ReasonCode.CLAIM_TARGET_MISSING in receipt.reason_codes


def test_claim_budget_demand_blocks_act() -> None:
    task = full_task()
    task = task.model_copy(
        update={"claim": ClaimSnapshot(requested_action="act", budget_demand=11)}
    )
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CLAIM_BUDGET_EXCEEDS_BUDGET in receipt.reason_codes


def test_claim_stake_demand_blocks_act() -> None:
    task = full_task()
    task = task.model_copy(
        update={"claim": ClaimSnapshot(requested_action="act", stake_demand=1)}
    )
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CLAIM_STAKE_EXCEEDS_POLICY in receipt.reason_codes


def test_missing_ambient_model_fails_closed_in_strict_mode() -> None:
    task = full_task()
    task = task.model_copy(update={"ambient_model": None})
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.AMBIENT_ACTION_MODEL_MISSING in receipt.reason_codes


def test_service_certificate_digests_empty_blocks_act() -> None:
    task = full_task()
    envelope = task.service_envelope.model_copy(update={"service_certificate_digests": []})
    receipt = decide(task=task.model_copy(update={"service_envelope": envelope}))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.SERVICE_CERTIFICATES_EMPTY in receipt.reason_codes


def test_public_state_budget_mismatch_blocks_act() -> None:
    task = full_task()
    public_state = task.public_state.model_copy(update={"budget_remaining": 9})  # type: ignore[union-attr]
    receipt = decide(task=task.model_copy(update={"public_state": public_state}))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.PUBLIC_STATE_BUDGET_MISMATCH in receipt.reason_codes


def test_public_state_horizon_mismatch_blocks_act() -> None:
    task = full_task()
    public_state = task.public_state.model_copy(update={"remaining_horizon": 2})  # type: ignore[union-attr]
    receipt = decide(task=task.model_copy(update={"public_state": public_state}))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.PUBLIC_STATE_HORIZON_MISMATCH in receipt.reason_codes


def test_controller_certificate_missing_blocks_act() -> None:
    task = full_task().model_copy(update={"controller_certificate": None})
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CONTROLLER_CERTIFICATE_MISSING in receipt.reason_codes


def test_controller_safe_set_empty_blocks_act() -> None:
    task = full_task().model_copy(
        update={
            "controller_certificate": ControllerCertificateSnapshot(
                feasibility_mask_digest=DIGEST,
                controller_certificate_digest=DIGEST,
                loss_model_digest=DIGEST,
                safe_policy_set_nonempty=False,
            )
        }
    )
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CONTROLLER_SAFE_SET_EMPTY in receipt.reason_codes


def test_missing_evidence_verifies_when_possible() -> None:
    receipt = decide(
        agent=AgentSnapshot(agent_id="agent", capabilities=["act"], verification_capability=True),
        evidence=EvidenceSnapshot(
            required_evidence=["e1"],
            verification_available=True,
            verification_portfolio=verification_portfolio(),
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
            stabilizability_certificate_digest=DIGEST,
        ),
        budget=CostBudget(budget_remaining=10, verification_cost_upper_bound=1),
    )
    assert receipt.decision == ParticipationDecision.VERIFY
    assert ReasonCode.EVIDENCE_MISSING in receipt.reason_codes


def test_missing_evidence_does_not_act_without_verification() -> None:
    receipt = decide(
        evidence=EvidenceSnapshot(
            required_evidence=["e1"],
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
        )
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.EVIDENCE_MISSING in receipt.reason_codes


def test_missing_capability_assists_without_authority_expansion() -> None:
    receipt = decide(
        agent=AgentSnapshot(agent_id="agent", capabilities=[], assist_capabilities=["act"])
    )
    assert receipt.decision == ParticipationDecision.ASSIST
    assert ReasonCode.ASSIST_AUTHORITY_NOT_EXPANDED in receipt.reason_codes


def test_protected_action_still_refuses_even_if_assist_possible() -> None:
    receipt = decide(
        task=TaskSnapshot(
            task_id="t1",
            requested_action="write_file",
            protected_action=True,
            claim=ClaimSnapshot(requested_action="write_file", protected_action=True),
        ),
        agent=AgentSnapshot(agent_id="agent", capabilities=[], assist_capabilities=["write_file"]),
        authority=AuthoritySnapshot(actor="agent"),
    )
    assert receipt.decision == ParticipationDecision.REFUSE


def test_high_harm_exits_by_default() -> None:
    receipt = decide(uncertainty=UncertaintyEnvelope(harm_upper_bound=0.9))
    assert receipt.decision == ParticipationDecision.EXIT


def test_requested_verify_returns_verify() -> None:
    receipt = decide(
        task=full_task(role=ClaimRole.VERIFY),
        agent=AgentSnapshot(agent_id="agent", verification_capability=True),
        authority=AuthoritySnapshot(
            actor="agent",
            permitted_actions=["act"],
            valid=True,
            authority_digest=DIGEST,
        ),
        evidence=EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            verification_portfolio=verification_portfolio(),
        ),
        budget=CostBudget(budget_remaining=10),
    )
    assert receipt.decision == ParticipationDecision.VERIFY


def test_requested_withdraw_ignores_task_evidence_gaps_after_strict_entry_checks() -> None:
    receipt = decide(
        task=full_task(role=ClaimRole.WITHDRAW),
        evidence=EvidenceSnapshot(
            required_evidence=["e1"],
            replayable=False,
            certificates_nonempty=True,
        ),
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert receipt.reason_codes == [ReasonCode.WITHDRAW_CONDITIONS_SATISFIED]


def test_requested_exit_ignores_capability_success_after_strict_entry_checks() -> None:
    receipt = decide(
        task=full_task(role=ClaimRole.EXIT),
        agent=AgentSnapshot(agent_id="agent", capabilities=[], capability_lower_bound=0),
        uncertainty=UncertaintyEnvelope(success_lower_bound=0),
    )
    assert receipt.decision == ParticipationDecision.EXIT
    assert receipt.reason_codes == [ReasonCode.EXIT_CONDITIONS_SATISFIED]


def test_requested_verify_uses_portfolio_before_task_evidence_gate() -> None:
    receipt = decide(
        task=full_task(role=ClaimRole.VERIFY),
        agent=AgentSnapshot(agent_id="agent", verification_capability=True),
        evidence=EvidenceSnapshot(
            required_evidence=["e1"],
            replayable=False,
            certificates_nonempty=True,
            verification_portfolio=verification_portfolio(),
        ),
    )
    assert receipt.decision == ParticipationDecision.VERIFY
    assert receipt.reason_codes == [ReasonCode.VERIFICATION_CAPACITY_AVAILABLE]


def test_continue_maps_to_act_with_continue_reason() -> None:
    task = full_task(role=ClaimRole.CONTINUE)
    receipt = decide(
        task=task,
        agent=AgentSnapshot(agent_id="agent", capabilities=["continue"], capability_lower_bound=1),
    )
    assert receipt.decision == ParticipationDecision.ACT
    assert ReasonCode.CONTINUE_CONDITIONS_SATISFIED in receipt.reason_codes


def test_submission_harm_blocks_act() -> None:
    receipt = decide(attribution=AttributionState(submission_harm_upper_bound=0.9))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.SUBMISSION_HARM_EXCEEDS_LIMIT in receipt.reason_codes


def test_capability_lower_bound_blocks_act() -> None:
    receipt = decide(
        agent=AgentSnapshot(
            agent_id="agent",
            capabilities=["act"],
            capability_lower_bound=0.1,
        )
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CAPABILITY_LOWER_BOUND_INSUFFICIENT in receipt.reason_codes


def test_require_stabilizable_blocks_when_missing() -> None:
    receipt = decide(
        evidence=EvidenceSnapshot(replayable=True, certificates_nonempty=True),
        policy=ParticipationPolicy(require_stabilizable=True),
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.STABILIZABILITY_MISSING in receipt.reason_codes


def test_require_stabilizable_blocks_when_certificate_missing() -> None:
    receipt = decide(
        evidence=EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
        ),
        policy=ParticipationPolicy(require_stabilizable=True),
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.STABILIZABILITY_CERTIFICATE_MISSING in receipt.reason_codes


def test_required_corroboration_blocks_when_missing() -> None:
    receipt = decide(
        evidence=EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
            stabilizability_certificate_digest=DIGEST,
        ),
        policy=ParticipationPolicy(require_corroboration=True),
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CORROBORATION_CERTIFICATE_MISSING in receipt.reason_codes


def test_service_fault_certificate_missing_blocks_act() -> None:
    receipt = decide(
        uncertainty=UncertaintyEnvelope(
            success_lower_bound=1,
            service_faults={"epsilon_post": 0.1},
        )
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.SERVICE_FAULT_CERTIFICATE_MISSING in receipt.reason_codes


def test_zero_service_fault_certificate_missing_blocks_strict_act() -> None:
    receipt = decide(uncertainty=UncertaintyEnvelope(success_lower_bound=1))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.SERVICE_FAULT_CERTIFICATE_MISSING in receipt.reason_codes


def test_controller_certificate_lineage_mismatch_blocks_act() -> None:
    other_digest = "sha256:" + "1" * 64
    task = full_task().model_copy(
        update={
            "controller_certificate": ControllerCertificateSnapshot(
                feasibility_mask_digest=DIGEST,
                controller_certificate_digest=other_digest,
                loss_model_digest=DIGEST,
                safe_policy_set_nonempty=True,
            )
        }
    )
    receipt = decide(task=task)
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_LINEAGE_MISMATCH in receipt.reason_codes


def test_participation_interface_lineage_mismatch_blocks_act() -> None:
    other_digest = "sha256:" + "1" * 64
    task = full_task()
    interface = task.participation_interface.model_copy(  # type: ignore[union-attr]
        update={"certificate_digests": [other_digest]}
    )
    receipt = decide(task=task.model_copy(update={"participation_interface": interface}))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_LINEAGE_MISMATCH in receipt.reason_codes


def test_participation_interface_named_certificate_lineage_mismatch_blocks_act() -> None:
    other_digest = "sha256:" + "1" * 64
    task = full_task()
    interface = task.participation_interface.model_copy(  # type: ignore[union-attr]
        update={"omitted_deviation_certificate_digest": other_digest}
    )
    receipt = decide(task=task.model_copy(update={"participation_interface": interface}))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_LINEAGE_MISMATCH in receipt.reason_codes


def test_verification_portfolio_certificate_missing_is_detected_by_lineage() -> None:
    portfolio = verification_portfolio().model_copy(update={"portfolio_certificate_digest": None})
    receipt = decide(
        evidence=EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
            stabilizability_certificate_digest=DIGEST,
            verification_portfolio=portfolio,
        )
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_DIGEST_MISSING in receipt.reason_codes


def test_stabilizability_lineage_mismatch_blocks_act() -> None:
    other_digest = "sha256:" + "1" * 64
    receipt = decide(
        evidence=EvidenceSnapshot(
            replayable=True,
            certificates_nonempty=True,
            stabilizable_certified=True,
            stabilizability_certificate_digest=other_digest,
        )
    )
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_LINEAGE_MISMATCH in receipt.reason_codes


def test_corroboration_lineage_mismatch_blocks_act_when_declared() -> None:
    other_digest = "sha256:" + "1" * 64
    base_evidence = full_inputs()["evidence"]
    corroboration = base_evidence.corroboration.model_copy(  # type: ignore[union-attr]
        update={"covariance_certificate_digests": [other_digest]}
    )
    evidence = base_evidence.model_copy(update={"corroboration": corroboration})  # type: ignore[union-attr]
    receipt = decide(evidence=evidence, policy=ParticipationPolicy(require_corroboration=True))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.CERTIFICATE_LINEAGE_MISMATCH in receipt.reason_codes


def test_external_certificate_policy_allows_lineage_digest() -> None:
    other_digest = "sha256:" + "1" * 64
    task = full_task().model_copy(
        update={
            "controller_certificate": ControllerCertificateSnapshot(
                feasibility_mask_digest=DIGEST,
                controller_certificate_digest=other_digest,
                loss_model_digest=DIGEST,
                safe_policy_set_nonempty=True,
            )
        }
    )
    receipt = decide(
        task=task,
        policy=ParticipationPolicy(external_certificate_digests=[other_digest]),
    )
    assert receipt.decision == ParticipationDecision.ACT


def test_verify_on_ineligible_snapshot_false_withdraws() -> None:
    task = full_task()
    task = task.model_copy(update={"public_state": None})
    receipt = decide(task=task, policy=ParticipationPolicy(verify_on_ineligible_snapshot=False))
    assert receipt.decision == ParticipationDecision.WITHDRAW
    assert ReasonCode.PUBLIC_COORDINATION_STATE_MISSING in receipt.reason_codes
