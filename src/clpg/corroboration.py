"""Declared corroboration-certificate checks."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import ReasonCode


def evaluate_corroboration(ctx: DecisionContext) -> DecisionOutcome | None:
    if not ctx.policy.require_corroboration:
        return None

    corroboration = ctx.evidence.corroboration
    if corroboration is None or not corroboration.covariance_certificate_digests:
        ctx.add_check(
            "corroboration_covariance_certificates_declared",
            False,
            ReasonCode.CORROBORATION_CERTIFICATE_MISSING,
        )
        return ctx.degrade(
            ReasonCode.CORROBORATION_CERTIFICATE_MISSING,
            "corroboration_certificate_missing",
        )
    ctx.add_check("corroboration_covariance_certificates_declared", True)

    if corroboration.active_block_count <= 0:
        ctx.add_check(
            "corroboration_active_blocks_nonempty",
            False,
            ReasonCode.CORROBORATION_CERTIFICATE_MISSING,
            observed={"active_block_count": corroboration.active_block_count},
        )
        return ctx.degrade(
            ReasonCode.CORROBORATION_CERTIFICATE_MISSING,
            "corroboration_active_blocks_empty",
        )
    ctx.add_check("corroboration_active_blocks_nonempty", True)

    if corroboration.effective_size_lower_bound < ctx.policy.min_corroboration_effective_size:
        ctx.add_check(
            "corroboration_effective_size_sufficient",
            False,
            ReasonCode.CORROBORATION_EFFECTIVE_SIZE_INSUFFICIENT,
            observed={
                "effective_size_lower_bound": corroboration.effective_size_lower_bound
            },
            threshold={
                "min_corroboration_effective_size": (
                    ctx.policy.min_corroboration_effective_size
                )
            },
        )
        return ctx.degrade(
            ReasonCode.CORROBORATION_EFFECTIVE_SIZE_INSUFFICIENT,
            "corroboration_effective_size_insufficient",
        )
    ctx.add_check("corroboration_effective_size_sufficient", True)

    if corroboration.observable_separation_lower_bound < ctx.policy.min_observable_separation:
        ctx.add_check(
            "corroboration_observable_separation_sufficient",
            False,
            ReasonCode.CORROBORATION_SEPARATION_INSUFFICIENT,
            observed={
                "observable_separation_lower_bound": (
                    corroboration.observable_separation_lower_bound
                )
            },
            threshold={"min_observable_separation": ctx.policy.min_observable_separation},
        )
        return ctx.degrade(
            ReasonCode.CORROBORATION_SEPARATION_INSUFFICIENT,
            "corroboration_separation_insufficient",
        )
    ctx.add_check("corroboration_observable_separation_sufficient", True)
    return None
