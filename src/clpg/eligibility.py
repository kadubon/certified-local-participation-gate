"""Decision-eligible snapshot checks."""

from __future__ import annotations

from datetime import timezone

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import PolicyMode, ReasonCode


def evaluate_eligibility(ctx: DecisionContext) -> DecisionOutcome | None:
    if ctx.policy.mode == PolicyMode.DEMO:
        ctx.add_check(
            "demo_mode_skips_strict_snapshot_eligibility",
            True,
            observed={"mode": ctx.policy.mode},
        )
        return None

    if ctx.policy.require_public_coordination_state and ctx.task.public_state is None:
        ctx.add_check(
            "public_coordination_state_declared",
            False,
            ReasonCode.PUBLIC_COORDINATION_STATE_MISSING,
        )
        return ctx.degrade(
            ReasonCode.PUBLIC_COORDINATION_STATE_MISSING,
            "public_coordination_state_missing",
        )
    ctx.add_check("public_coordination_state_declared", True)

    envelope = ctx.task.service_envelope
    if not envelope.certificates_verified:
        ctx.add_check(
            "snapshot_certificates_verified",
            False,
            ReasonCode.SNAPSHOT_CERTIFICATES_INVALID,
        )
        return ctx.degrade(
            ReasonCode.SNAPSHOT_CERTIFICATES_INVALID,
            "snapshot_certificates_invalid",
        )
    ctx.add_check("snapshot_certificates_verified", True)

    if ctx.policy.require_service_certificate_digests and not envelope.service_certificate_digests:
        ctx.add_check(
            "service_certificate_digests_declared",
            False,
            ReasonCode.SERVICE_CERTIFICATES_EMPTY,
        )
        return ctx.degrade(
            ReasonCode.SERVICE_CERTIFICATES_EMPTY,
            "service_certificates_empty",
        )
    ctx.add_check("service_certificate_digests_declared", True)

    if ctx.policy.require_explicit_service_expiry and envelope.expires_at is None:
        ctx.add_check("snapshot_expiry_declared", False, ReasonCode.SNAPSHOT_EXPIRY_MISSING)
        return ctx.degrade(ReasonCode.SNAPSHOT_EXPIRY_MISSING, "snapshot_expiry_missing")
    ctx.add_check("snapshot_expiry_declared", True)

    if envelope.expires_at is not None:
        expires_at = envelope.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= ctx.now:
            ctx.add_check(
                "snapshot_not_expired",
                False,
                ReasonCode.SNAPSHOT_EXPIRED,
                observed={"expires_at": expires_at.isoformat(), "now": ctx.now.isoformat()},
            )
            return ctx.degrade(ReasonCode.SNAPSHOT_EXPIRED, "snapshot_expired")
    ctx.add_check("snapshot_not_expired", True)

    if envelope.snapshot_staleness_seconds > ctx.policy.max_snapshot_staleness_seconds:
        ctx.add_check(
            "snapshot_staleness_within_tolerance",
            False,
            ReasonCode.SNAPSHOT_STALENESS_EXCEEDS_TOLERANCE,
            observed={"snapshot_staleness_seconds": envelope.snapshot_staleness_seconds},
            threshold={
                "max_snapshot_staleness_seconds": ctx.policy.max_snapshot_staleness_seconds
            },
        )
        return ctx.degrade(
            ReasonCode.SNAPSHOT_STALENESS_EXCEEDS_TOLERANCE,
            "snapshot_staleness_exceeds_tolerance",
        )
    ctx.add_check("snapshot_staleness_within_tolerance", True)

    if not envelope.posterior_family_nonempty:
        ctx.add_check("posterior_family_nonempty", False, ReasonCode.POSTERIOR_FAMILY_EMPTY)
        return ctx.degrade(ReasonCode.POSTERIOR_FAMILY_EMPTY, "posterior_family_empty")
    ctx.add_check("posterior_family_nonempty", True)

    if not envelope.derived_certificate_families_nonempty or not ctx.evidence.certificates_nonempty:
        ctx.add_check(
            "derived_certificate_families_nonempty",
            False,
            ReasonCode.DERIVED_CERTIFICATE_FAMILY_EMPTY,
            observed={
                "service_derived_nonempty": envelope.derived_certificate_families_nonempty,
                "evidence_certificates_nonempty": ctx.evidence.certificates_nonempty,
            },
        )
        return ctx.degrade(
            ReasonCode.DERIVED_CERTIFICATE_FAMILY_EMPTY,
            "derived_certificate_family_empty",
        )
    ctx.add_check("derived_certificate_families_nonempty", True)

    if (
        ctx.policy.require_audited_participation_interface
        and ctx.task.participation_interface is None
    ):
        ctx.add_check(
            "audited_participation_interface_declared",
            False,
            ReasonCode.PARTICIPATION_INTERFACE_MISSING,
        )
        return ctx.degrade(
            ReasonCode.PARTICIPATION_INTERFACE_MISSING,
            "participation_interface_missing",
        )
    ctx.add_check("audited_participation_interface_declared", True)
    return None
