from __future__ import annotations

import pytest

from l9_observability_core import EvidenceKind, EvidenceRef


def test_evidence_digest_requires_canonical_algorithm_prefix() -> None:
    digest = "a" * 64
    with pytest.raises(ValueError):
        EvidenceRef(kind=EvidenceKind.ARTIFACT, ref="artifact.json", digest=digest)
    ref = EvidenceRef(kind=EvidenceKind.ARTIFACT, ref="artifact.json", digest="sha256:" + digest)
    assert ref.digest == "sha256:" + digest


def test_evidence_ref_rejects_whitespace_only() -> None:
    with pytest.raises(ValueError):
        EvidenceRef(kind=EvidenceKind.OTHER, ref="   ")
