"""Certificate lineage checks over declared service certificate families."""

from __future__ import annotations

from clpg.engine import DecisionContext, DecisionOutcome
from clpg.enums import PolicyMode, ReasonCode


def _declared_certificate_digests(ctx: DecisionContext) -> dict[str, str | None]:
    task = ctx.task
    evidence = ctx.evidence
    digests: dict[str, str | None] = {}

    if task.participation_interface is not None:
        for index, digest in enumerate(task.participation_interface.certificate_digests):
            digests[f"participation_interface.certificate_digests[{index}]"] = digest
        if task.participation_interface.coverage_certificate_digest is not None:
            digests["participation_interface.coverage_certificate_digest"] = (
                task.participation_interface.coverage_certificate_digest
            )
        if task.participation_interface.stability_certificate_digest is not None:
            digests["participation_interface.stability_certificate_digest"] = (
                task.participation_interface.stability_certificate_digest
            )
        if task.participation_interface.omitted_deviation_certificate_digest is not None:
            digests["participation_interface.omitted_deviation_certificate_digest"] = (
                task.participation_interface.omitted_deviation_certificate_digest
            )
    if task.controller_certificate is not None:
        if (
            task.controller_certificate.controller_certificate_digest is None
            and task.controller_certificate.controller_sketch_digest is None
        ):
            digests["controller_certificate.controller_certificate_digest"] = None
        if task.controller_certificate.controller_certificate_digest is not None:
            digests["controller_certificate.controller_certificate_digest"] = (
                task.controller_certificate.controller_certificate_digest
            )
        if task.controller_certificate.controller_sketch_digest is not None:
            digests["controller_certificate.controller_sketch_digest"] = (
                task.controller_certificate.controller_sketch_digest
            )
    if evidence.verification_portfolio is not None:
        digests["verification_portfolio.portfolio_certificate_digest"] = (
            evidence.verification_portfolio.portfolio_certificate_digest
        )
    if evidence.stabilizability_certificate_digest is not None:
        digests["evidence.stabilizability_certificate_digest"] = (
            evidence.stabilizability_certificate_digest
        )
    if evidence.corroboration is not None:
        for index, digest in enumerate(evidence.corroboration.covariance_certificate_digests):
            digests[f"corroboration.covariance_certificate_digests[{index}]"] = digest
    if ctx.uncertainty.service_faults.fault_profile_digest is not None:
        digests["service_faults.fault_profile_digest"] = (
            ctx.uncertainty.service_faults.fault_profile_digest
        )
    return digests


def evaluate_certificate_lineage(ctx: DecisionContext) -> DecisionOutcome | None:
    if ctx.policy.mode == PolicyMode.DEMO:
        return None

    declared = _declared_certificate_digests(ctx)
    missing = sorted(name for name, digest in declared.items() if digest is None)
    if missing:
        ctx.add_check(
            "declared_certificate_digests_present",
            False,
            ReasonCode.CERTIFICATE_DIGEST_MISSING,
            observed={"missing_certificate_digests": missing},
        )
        return ctx.degrade(
            ReasonCode.CERTIFICATE_DIGEST_MISSING,
            "certificate_digest_missing",
        )
    ctx.add_check("declared_certificate_digests_present", True)

    allowed = set(ctx.task.service_envelope.service_certificate_digests)
    allowed.update(ctx.policy.external_certificate_digests)
    mismatches = {
        name: digest
        for name, digest in declared.items()
        if digest is not None and digest not in allowed
    }
    if mismatches:
        ctx.add_check(
            "certificate_lineage_matches_service_family",
            False,
            ReasonCode.CERTIFICATE_LINEAGE_MISMATCH,
            observed={"lineage_mismatches": mismatches},
        )
        return ctx.degrade(
            ReasonCode.CERTIFICATE_LINEAGE_MISMATCH,
            "certificate_lineage_mismatch",
        )
    ctx.add_check("certificate_lineage_matches_service_family", True)
    return None
