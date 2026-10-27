# Product Breakdown - ssp_references

Canonical current state for the SSP reference fixture repository: why it exists, what it promises, how it is organized, and how it is checked.

## The Seven Layers

- `00-intent/` - why the project exists, who it serves.
- `01-product/` - promised capabilities and scope.
- `02-architecture/` - how deliverables, evidence, and work are organized.
- `03-implementation/` - concrete authoring, build, and runtime assets.
- `04-verification/` - how claims are checked.
- `05-operation/` - how authors run, maintain, and release.
- `06-evolution/` - candidates for controlled change.
- the decision archive (`../archive/archive.zip`) - flat, dated history, read via `pb archive`, never browsed.

## Boundary Rule

Current state lives in layer leaves. History lives in `../archive/archive.zip`. Registers are generated (`../archive/README.md`, `../archive/design-choice-log.md`, `../archive/traceability-map.md`) with `pb registers --root docs/breakdown`; never edit them by hand.

Information flows downward only: Intent, Product, Architecture, Implementation, Verification, Operation. Evolution holds candidates, never current state.

## Excludes

- Dated rationale in layer leaves: use `pb archive`.
- Implementation detail in high layers: route to the owning layer.
- Hand-maintained decision logs or traceability maps: regenerate with `pb registers`.
