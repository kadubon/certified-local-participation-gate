"""Controller-certificate checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import PolicyMode, ReasonCode


def evaluate_controller_certificate(ctx: DecisionContext) -> DecisionOutcome | None:
    if ctx.policy.mode == PolicyMode.DEMO or not ctx.policy.require_controller_certificate:
        return None

    certificate = ctx.task.controller_certificate
    if certificate is None:
        ctx.add_check(
            "controller_certificate_declared",
            False,
            ReasonCode.CONTROLLER_CERTIFICATE_MISSING,
        )
        return ctx.degrade(
            ReasonCode.CONTROLLER_CERTIFICATE_MISSING,
            "controller_certificate_missing",
        )
    ctx.add_check("controller_certificate_declared", True)

    if not certificate.controller_certificate_digest and not certificate.controller_sketch_digest:
        ctx.add_check(
            "controller_certificate_or_sketch_digest_declared",
            False,
            ReasonCode.CONTROLLER_CERTIFICATE_MISSING,
        )
        return ctx.degrade(
            ReasonCode.CONTROLLER_CERTIFICATE_MISSING,
            "controller_certificate_digest_missing",
        )
    ctx.add_check("controller_certificate_or_sketch_digest_declared", True)

    if ctx.task.ambient_model is not None:
        mask_matches = (
            certificate.feasibility_mask_digest == ctx.task.ambient_model.feasibility_mask_digest
        )
        if not mask_matches:
            ctx.add_check(
                "controller_feasibility_mask_matches_ambient_model",
                False,
                ReasonCode.CONTROLLER_FEASIBILITY_DIGEST_MISMATCH,
                observed={
                    "controller_feasibility_mask_digest": certificate.feasibility_mask_digest,
                    "ambient_feasibility_mask_digest": (
                        ctx.task.ambient_model.feasibility_mask_digest
                    ),
                },
            )
            return ctx.degrade(
                ReasonCode.CONTROLLER_FEASIBILITY_DIGEST_MISMATCH,
                "controller_feasibility_digest_mismatch",
            )
    ctx.add_check("controller_feasibility_mask_matches_ambient_model", True)

    if not certificate.safe_policy_set_nonempty:
        ctx.add_check(
            "controller_safe_policy_set_nonempty",
            False,
            ReasonCode.CONTROLLER_SAFE_SET_EMPTY,
        )
        return ctx.degrade(
            ReasonCode.CONTROLLER_SAFE_SET_EMPTY,
            "controller_safe_set_empty",
        )
    ctx.add_check("controller_safe_policy_set_nonempty", True)
    return None
