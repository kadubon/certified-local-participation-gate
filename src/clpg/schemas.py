"""JSON Schema export."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from clpg.canonical import canonical_json
from clpg.models import (
    AgentSnapshot,
    AmbientActionModel,
    AttributionState,
    AuditedParticipationInterface,
    AuthoritySnapshot,
    ClaimSnapshot,
    ConformanceCase,
    ControllerCertificateSnapshot,
    CorroborationSnapshot,
    CostBudget,
    EvidenceSnapshot,
    LedgerRecord,
    ParticipationPolicy,
    ParticipationReceipt,
    PublicCoordinationState,
    TaskSnapshot,
    UncertaintyEnvelope,
    VerificationPortfolioSnapshot,
)

SCHEMA_MODELS: dict[str, type[BaseModel]] = {
    "TaskSnapshot": TaskSnapshot,
    "ClaimSnapshot": ClaimSnapshot,
    "PublicCoordinationState": PublicCoordinationState,
    "AmbientActionModel": AmbientActionModel,
    "AuditedParticipationInterface": AuditedParticipationInterface,
    "ControllerCertificateSnapshot": ControllerCertificateSnapshot,
    "AgentSnapshot": AgentSnapshot,
    "AuthoritySnapshot": AuthoritySnapshot,
    "EvidenceSnapshot": EvidenceSnapshot,
    "CorroborationSnapshot": CorroborationSnapshot,
    "VerificationPortfolioSnapshot": VerificationPortfolioSnapshot,
    "UncertaintyEnvelope": UncertaintyEnvelope,
    "AttributionState": AttributionState,
    "CostBudget": CostBudget,
    "ParticipationPolicy": ParticipationPolicy,
    "ParticipationReceipt": ParticipationReceipt,
    "LedgerRecord": LedgerRecord,
    "ConformanceCase": ConformanceCase,
}


def export_json_schemas(output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {}
    for name, model in SCHEMA_MODELS.items():
        path = out / f"{name}.schema.json"
        path.write_text(canonical_json(model.model_json_schema()) + "\n", encoding="utf-8")
        manifest[name] = str(path)
    return manifest
