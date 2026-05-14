"""Stable enum values for CLPG public models."""

from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Small Python 3.10-compatible string enum base."""

    def __str__(self) -> str:
        return str(self.value)


class ClaimRole(StrEnum):
    NONE = "none"
    ACT = "act"
    ASSIST = "assist"
    VERIFY = "verify"
    WITHDRAW = "withdraw"
    EXIT = "exit"
    CONTINUE = "continue"


class ParticipationDecision(StrEnum):
    ACT = "act"
    ASSIST = "assist"
    VERIFY = "verify"
    WITHDRAW = "withdraw"
    EXIT = "exit"
    REFUSE = "refuse"
    ESCALATE = "escalate"


class ReasonCode(StrEnum):
    POLICY_DISALLOWS_TASK = "policy_disallows_task"
    TASK_MARKED_DISALLOWED = "task_marked_disallowed"
    PROTECTED_ACTION_WITHOUT_AUTHORITY = "protected_action_without_authority"
    AUTHORITY_MISSING = "authority_missing"
    AUTHORITY_SCOPE_MISMATCH = "authority_scope_mismatch"
    AUTHORITY_EXPIRED = "authority_expired"
    AUTHORITY_ACTOR_MISMATCH = "authority_actor_mismatch"
    AUTHORITY_CERTIFICATE_MISSING = "authority_certificate_missing"
    CLAIM_SNAPSHOT_MISSING = "claim_snapshot_missing"
    CLAIM_TARGET_MISSING = "claim_target_missing"
    CLAIM_LEGACY_FIELD_CONFLICT = "claim_legacy_field_conflict"
    PROTECTED_FLAG_CONFLICT = "protected_flag_conflict"
    NULL_CLAIM_WITHDRAWN = "null_claim_withdrawn"
    CLAIM_BUDGET_EXCEEDS_BUDGET = "claim_budget_exceeds_budget"
    CLAIM_STAKE_EXCEEDS_POLICY = "claim_stake_exceeds_policy"
    SNAPSHOT_CERTIFICATES_INVALID = "snapshot_certificates_invalid"
    SNAPSHOT_EXPIRY_MISSING = "snapshot_expiry_missing"
    SNAPSHOT_EXPIRED = "snapshot_expired"
    SNAPSHOT_STALENESS_EXCEEDS_TOLERANCE = "snapshot_staleness_exceeds_tolerance"
    SERVICE_CERTIFICATES_EMPTY = "service_certificates_empty"
    PUBLIC_COORDINATION_STATE_MISSING = "public_coordination_state_missing"
    PUBLIC_STATE_BUDGET_MISMATCH = "public_state_budget_mismatch"
    PUBLIC_STATE_HORIZON_MISMATCH = "public_state_horizon_mismatch"
    PARTICIPATION_INTERFACE_MISSING = "participation_interface_missing"
    POSTERIOR_FAMILY_EMPTY = "posterior_family_empty"
    DERIVED_CERTIFICATE_FAMILY_EMPTY = "derived_certificate_family_empty"
    AMBIENT_ACTION_MODEL_MISSING = "ambient_action_model_missing"
    FEASIBILITY_MASK_MISSING = "feasibility_mask_missing"
    ROLE_NOT_FEASIBLE = "role_not_feasible"
    ACTION_NOT_FEASIBLE = "action_not_feasible"
    CONTROLLER_CERTIFICATE_MISSING = "controller_certificate_missing"
    CONTROLLER_SAFE_SET_EMPTY = "controller_safe_set_empty"
    CONTROLLER_FEASIBILITY_DIGEST_MISMATCH = "controller_feasibility_digest_mismatch"
    CERTIFICATE_LINEAGE_MISMATCH = "certificate_lineage_mismatch"
    CERTIFICATE_DIGEST_MISSING = "certificate_digest_missing"
    CAPABILITY_MISSING = "capability_missing"
    CAPABILITY_LOWER_BOUND_INSUFFICIENT = "capability_lower_bound_insufficient"
    CAPABILITY_PARTIAL_ASSIST_POSSIBLE = "capability_partial_assist_possible"
    ASSIST_AUTHORITY_NOT_EXPANDED = "assist_authority_not_expanded"
    EVIDENCE_MISSING = "evidence_missing"
    CONTRADICTION_ACTIVE = "contradiction_active"
    REPLAYABILITY_MISSING = "replayability_missing"
    PROVENANCE_SUMMARY_MISSING = "provenance_summary_missing"
    ATTRIBUTION_INSUFFICIENT = "attribution_insufficient"
    BUNDLE_CONTRACTIVENESS_MISSING = "bundle_contractiveness_missing"
    STABILIZABILITY_MISSING = "stabilizability_missing"
    STABILIZABILITY_CERTIFICATE_MISSING = "stabilizability_certificate_missing"
    CORROBORATION_CERTIFICATE_MISSING = "corroboration_certificate_missing"
    CORROBORATION_EFFECTIVE_SIZE_INSUFFICIENT = "corroboration_effective_size_insufficient"
    CORROBORATION_SEPARATION_INSUFFICIENT = "corroboration_separation_insufficient"
    UNCERTAINTY_EXCEEDS_POLICY = "uncertainty_exceeds_policy"
    SUCCESS_LOWER_BOUND_INSUFFICIENT = "success_lower_bound_insufficient"
    SUBMISSION_HARM_EXCEEDS_LIMIT = "submission_harm_exceeds_limit"
    HARM_UPPER_BOUND_EXCEEDS_LIMIT = "harm_upper_bound_exceeds_limit"
    CONTROLLER_LOSS_EXCEEDS_LIMIT = "controller_loss_exceeds_limit"
    SERVICE_FAULT_BUDGET_EXCEEDED = "service_fault_budget_exceeded"
    SERVICE_FAULT_CERTIFICATE_MISSING = "service_fault_certificate_missing"
    COST_BUDGET_EXCEEDED = "cost_budget_exceeded"
    DEADLINE_INFEASIBLE = "deadline_infeasible"
    VERIFICATION_CAPACITY_AVAILABLE = "verification_capacity_available"
    VERIFICATION_CAPACITY_MISSING = "verification_capacity_missing"
    VERIFICATION_COST_EXCEEDS_BUDGET = "verification_cost_exceeds_budget"
    VERIFICATION_AMBIGUITY_EMPTY = "verification_ambiguity_empty"
    VERIFICATION_SAFE_SET_EMPTY = "verification_safe_set_empty"
    VERIFICATION_PORTFOLIO_CERTIFICATE_MISSING = "verification_portfolio_certificate_missing"
    VERIFICATION_AMBIENT_MODEL_MISSING = "verification_ambient_model_missing"
    WITHDRAW_CONDITIONS_SATISFIED = "withdraw_conditions_satisfied"
    EXIT_CONDITIONS_SATISFIED = "exit_conditions_satisfied"
    CONTINUE_CONDITIONS_SATISFIED = "continue_conditions_satisfied"
    ACT_CONDITIONS_SATISFIED = "act_conditions_satisfied"
    ESCALATION_POLICY_SELECTED = "escalation_policy_selected"


class PolicyMode(StrEnum):
    STRICT = "strict"
    DEMO = "demo"
