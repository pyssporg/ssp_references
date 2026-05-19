# Review Plan — Simulation Registry and Comparison Pipeline

These items were originally tracked in the planning file at the repository
root. They are now in the backlog as candidates for future scoped tasks. Each
needs a task contract before implementation begins.

## Review Items

1. **Registry coverage review** — Confirm which model/case/backend combinations
   should be kept in `artifacts/simulation_registry.json`.
2. **Backend adapter review** — Review `ssp4sim` and `OMSimulator` adapters
   against the current config shape and result CSV contract.
3. **Manifest field review** — Review `setup.json` and run manifest fields for
   anything still missing or redundant.
4. **Comparison metrics review** — Decide which summary metrics are gate-worthy
   versus diagnostic-only.
5. **Backend/case expansion** — Determine whether additional backends or model
   cases should be added to the registry once the first comparison path is
   stable.

## Open Questions

- Which summary metrics should become acceptance criteria?
- Which additional registry entries should be added?

---

*These items are candidates for future orchestrated tasks. They are not
approved for implementation without a scoped task contract.*