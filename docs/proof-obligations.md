# Proof Obligations

CLPG v0.1.1 consumes declared certificates and bounds. It does not generate
theorem-level certificates from the source paper.

Source paper DOI: [10.5281/zenodo.19394600](https://doi.org/10.5281/zenodo.19394600).

The package's local checks are proof-obligation consumers: they require
certificate digests, finite-set declarations, and declared bounds to be present
and mutually consistent. They do not construct the paper's controller proofs,
stability proofs, covariance proofs, or attribution certificates.

Read this document as the boundary between CLPG and upstream systems. CLPG can
reject or degrade a local decision when these records are missing. It cannot
manufacture those records, sign them, or verify their substantive truth.

Operators must supply independent evidence for:

- claim authenticity and role/action metadata;
- authority validity, actor binding, and authority receipt/digest binding;
- service certificate validity;
- service-fault profile certification, even when fault bounds are zero;
- public coordination state reconstruction;
- ambient action universe and feasibility mask reconstruction;
- derived certificate lineage from the service certificate family;
- controller certificate/sketch reconstruction and nonempty safe policy set;
- audited participation interface reconstruction;
- posterior-family non-emptiness;
- evidence replayability;
- verification portfolio ambiguity and safe decision set;
- attribution completeness and submission-harm bound;
- stabilizability and omitted-deviation certificates when policy requires them;
- corroboration covariance/effective-size/separation certificates when policy requires them.

If those records are missing or fail local checks, strict mode degrades to
`verify`, `withdraw`, `exit`, or `refuse`.

The package's receipt proves only that CLPG followed its deterministic local
procedure over the declared records. It does not prove that upstream
certificates are true, legally sufficient, or institutionally authorized.
