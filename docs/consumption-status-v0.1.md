# Consumption status in constellation v0.1

## What this library owns

`l9-observability-core` owns observation and event contracts, canonical
digests, and correlation validation. It is a backend-neutral Python utility
library.

It does **not** schedule, gate, admit, dispatch, retry, or mutate. This is not
a promise about intent — the package contains no mechanism to do any of those
things. It is frozen event models, canonicalisation, digesting, and
side-effect-free validators. `tests/test_control_authority_boundary.py` keeps
that true by asserting the public API exposes no control verb and that every
exported callable belongs to a contract family.

On retry specifically: `AttemptEvent.retry_reason` and `FailureEvent.retryable`
record what a producer observed. Describing a retry is a contract concern.
Owning the decision to retry is not, and no callable here implies otherwise.

## Consumption status: unconsumed

**No repository in the L9 CI debt constellation consumes this library in
v0.1.** It has no workflows and no consumers. It is available and optional, not
wired.

This is stated plainly because the alternative — a clean, well-specified
contract library sitting in an architecture diagram — reads as an active
component to anyone who has not searched for its importers. Being unconsumed is
not a defect; presenting it as integrated would be.

Two facts follow, and neither is a criticism of this repository:

- Nothing downstream would notice if this library's boundary drifted, which is
  why the boundary test above exists rather than relying on integration
  pressure.
- The constellation currently has three disjoint failure taxonomies with no
  mapping between them: this library's `FailureClass`, the debt resolver's
  classification categories, and the SDK's `ProviderFailureType`. Only
  `dependency` and `timeout` are shared strings. That is latent rather than
  active precisely because nothing routes failures between these components —
  it becomes a real divergence the moment they connect.

## If this library is adopted

The natural first step is the failure vocabulary. This repository is the sensible
owner: it already holds the event contracts and, by construction, no control
authority — so naming it the vocabulary owner does not concentrate decision-making
anywhere. Adoption would mean the other components declare an explicit mapping
into `FailureClass`, rather than each keeping a private taxonomy.

That is a v0.1+ decision. Nothing in this repository should be changed to
anticipate it.
