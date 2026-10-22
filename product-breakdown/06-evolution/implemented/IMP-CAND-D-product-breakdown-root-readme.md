# IMP-CAND-D: Product-Breakdown Root README

## Status

Proposed

## Layer

Implementation (03) — documentation navigation

## Theme

Documentation hierarchy entry point

## Evidence

- `.opencode/templates/product-breakdown/README.md` exists but is not deployed
- `glob("product-breakdown/README.md")` returns nothing
- Navigators land in directory listing with no explanation

## Current Pain Or Risk

The product-breakdown tree is the repository's documentation backbone, but has no landing page. Navigators see `00-intent/`, `01-product/`, etc. without explanation of what these layers contain, how they relate, or how to navigate them. The template at `.opencode/templates/product-breakdown/README.md` has the needed structure ready to deploy.

## Proposed Improvement

Create `product-breakdown/README.md` modeled after the template at `.opencode/templates/product-breakdown/README.md`. Include: layer table with descriptions and links, layer questions, a "how to use this directory" section, and cross-references to `decision-log.md`, `naming.md`, `traceability-map.md`.

## Expected Benefit

First-time navigators of the documentation tree immediately understand its structure, purpose, and navigation paths.

## Risk And Blast Radius

Low. Single new file. Content already exists in the template.

## Suggested Priority

High

## Task Contract Seed

Create `product-breakdown/README.md` using `.opencode/templates/product-breakdown/README.md` as source. Deploy full content adjusting paths to match the repository. Include 7-layer table, layer questions, agent usage guidance, links to decision-log.md, naming.md, traceability-map.md.

## Out Of Scope

Modifying any layer's content. Adding decisions or trace entries.

## Traceability

- Architecture: Layer references align with `02-architecture/architecture.md` boundaries
- Implementation: Follows the existing template structure