# API Stability

Stable v0.1.x imports are exported from `clpg`, including the strict-mode
certificate summary models `ControllerCertificateSnapshot` and
`CorroborationSnapshot`.

Internal helpers in the modular evaluator files may change without deprecation before a later stable release. The public compatibility target is the Pydantic model and top-level `decide_participation` API, not private rule function names.
