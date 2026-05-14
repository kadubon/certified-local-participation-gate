"""Evidence and audited-attribution checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ReasonCode


def _missing_evidence(ctx: DecisionContext) -> list[str]:
    available = {block.evidence_id for block in ctx.evidence.evidence_blocks}
    declared_missing = list(ctx.evidence.missing_required_evidence)
    computed_missing = [
        item for item in ctx.evidence.required_evidence if item not in available
    ]
    return list(dict.fromkeys([*declared_missing, *computed_missing]))


def evaluate_evidence(ctx: DecisionContext) -> DecisionOutcome | None:
    missing = _missing_evidence(ctx)
    if ctx.policy.strict_evidence and missing:
        ctx.add_check(
            "required_evidence_present",
            False,
            ReasonCode.EVIDENCE_MISSING,
            observed={"missing_required_evidence": missing},
        )
        return ctx.degrade(ReasonCode.EVIDENCE_MISSING, "evidence_missing")
    ctx.add_check("required_evidence_present", True)

    if ctx.evidence.contradiction_active:
        ctx.add_check("no_active_contradiction", False, ReasonCode.CONTRADICTION_ACTIVE)
        return ctx.degrade(ReasonCode.CONTRADICTION_ACTIVE, "contradiction_active")
    ctx.add_check("no_active_contradiction", True)

    if ctx.policy.require_replayability and not ctx.evidence.replayable:
        ctx.add_check("evidence_replayable", False, ReasonCode.REPLAYABILITY_MISSING)
        return ctx.degrade(ReasonCode.REPLAYABILITY_MISSING, "replayability_missing")
    ctx.add_check("evidence_replayable", True)

    if ctx.policy.require_attribution and not ctx.attribution.attribution_complete:
        ctx.add_check("attribution_complete", False, ReasonCode.ATTRIBUTION_INSUFFICIENT)
        return ctx.degrade(
            ReasonCode.ATTRIBUTION_INSUFFICIENT,
            "attribution_insufficient",
        )
    ctx.add_check("attribution_complete", True)

    if (
        ctx.policy.require_bundle_contractiveness
        and not ctx.attribution.bundle_contractive_certified
    ):
        ctx.add_check(
            "bundle_contractive_certified",
            False,
            ReasonCode.BUNDLE_CONTRACTIVENESS_MISSING,
        )
        return ctx.degrade(
            ReasonCode.BUNDLE_CONTRACTIVENESS_MISSING,
            "bundle_contractiveness_missing",
        )
    ctx.add_check("bundle_contractive_certified", True)

    if ctx.policy.require_stabilizable and not ctx.evidence.stabilizable_certified:
        ctx.add_check("stabilizable_certified", False, ReasonCode.STABILIZABILITY_MISSING)
        return ctx.degrade(ReasonCode.STABILIZABILITY_MISSING, "stabilizability_missing")
    ctx.add_check("stabilizable_certified", True)

    if ctx.policy.require_stabilizable:
        interface_digest = (
            ctx.task.participation_interface.stability_certificate_digest
            if ctx.task.participation_interface is not None
            else None
        )
        if ctx.evidence.stabilizability_certificate_digest is None or interface_digest is None:
            ctx.add_check(
                "stabilizability_certificate_declared",
                False,
                ReasonCode.STABILIZABILITY_CERTIFICATE_MISSING,
                observed={
                    "evidence_stabilizability_certificate_digest": (
                        ctx.evidence.stabilizability_certificate_digest
                    ),
                    "interface_stability_certificate_digest": interface_digest,
                },
            )
            return ctx.degrade(
                ReasonCode.STABILIZABILITY_CERTIFICATE_MISSING,
                "stabilizability_certificate_missing",
            )
    ctx.add_check("stabilizability_certificate_declared", True)
    return None
