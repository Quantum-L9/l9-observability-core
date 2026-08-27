# Evidence and Provenance

## Purpose

`EvidenceRef` binds an observation to evidence metadata without making this package an artifact store,
resolver, authorization layer, or provenance database.

## Field semantics

| Field | Meaning |
|---|---|
| `kind` | Bounded evidence category. |
| `ref` | Producer/owner supplied reference string. It may be symbolic or resolvable depending on the external owner. |
| `digest` | Optional immutable SHA-256 content identity in canonical `sha256:<hex>` form. |
| `revision` | Optional immutable or versioned revision identity when the evidence owner has one. |
| `media_type` | Optional declared media type. |

The core validates shape and digest syntax. It does not dereference `ref`, prove that a revision exists,
or assert that bytes matching `digest` remain retrievable.

## Evidence capability levels

Consumers should distinguish these evidence states:

1. **Bound**: the event carries an `EvidenceRef`.
2. **Content-bound**: `digest` is present and identifies expected bytes.
3. **Resolvable**: an external owner can resolve `ref` and/or `revision` to evidence bytes.
4. **Verified**: resolved bytes have been hashed and match the canonical `digest`.

A digest by itself is strong content identity, but not durable retrievability. A symbolic reference by itself
is not an immutable locator.

## Producer rules

- Include a digest when the producer has authoritative bytes and can compute it without semantic ambiguity.
- Include a revision only when it is owned by the referenced system.
- Do not invent globally unique locations for evidence that is only locally available.
- Do not place credentials, authorization headers, secret-bearing request bodies, or unrestricted payloads in `ref`.
- Preserve the canonical evidence metadata unchanged through downstream projection.

## Resolver ownership

Evidence resolution belongs to the system that owns the artifact or durable evidence plane. A resolver may
be content-addressed, revision-addressed, repository-backed, object-store-backed, or another governed
mechanism. This core intentionally defines no resolver protocol because no single storage/authorization
contract has been proven common across L9 evidence owners.

## Durable verification pattern

A downstream evidence owner that claims durable verification SHOULD prove:

```text
canonical event
  -> EvidenceRef(ref, revision, digest)
  -> resolve using owning evidence system
  -> obtain immutable bytes
  -> SHA-256 bytes
  -> compare to EvidenceRef.digest
```

Successful resolution/verification may produce separate receipts. Those receipts remain owned by the
external evidence/admission system and do not mutate the original observation.
