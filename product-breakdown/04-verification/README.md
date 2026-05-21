# Verification

This directory holds verification artifacts for the `ssp_references` repository.
It sits at the **Verification** layer in the documentation chain, between
[03-implementation/](../03-implementation/) (Implementation) and the
completion gate.

Per KM-005, the Verification layer describes how the system is tested and
verified against its requirements. These documents are not implementation
instructions — they describe *how to verify* that the implementation works
correctly.

## Documents

| Document | Description |
|----------|-------------|
| [co_simulation_test_strategy.md](./co_simulation_test_strategy.md) | Overall test strategy: fixture classes, oracles, fixture-to-strategy mapping, and the three-step test flow (prepare, simulate, compare). |
| [co_simulation_fixture_mapping.md](./co_simulation_fixture_mapping.md) | Concrete mapping of fixtures to the test strategy, including custom composite fixtures for signal-propagation coverage. |
| [backend_adapter_review.md](./backend_adapter_review.md) | Contract review of ssp4sim and OMSimulator backend adapters against config shape and result CSV contract (IMP-CAND-H). |

## Backward Trace

These verification artifacts satisfy the System Architecture described in
[02-architecture/architecture.md](../02-architecture/architecture.md),
the [Product Decisions](../01-product/README.md) that translate intent
into durable promises, and the product commitments in
[00-intent/intent.md](../00-intent/intent.md). They trace backward through
the full documentation chain (Intent → Product Decisions → System Architecture →
Technical Decisions) — they do not link down into implementation details.
