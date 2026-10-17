# Validation record

Checked on 17 October 2026.

- Eight Python tests pass: conflicting IDs, legitimate co-location, axis-swap quarantine, non-finite coordinates, normalized duplicates, distance units, missing access data, and end-to-end reconciliation/reproducibility.
- Bundled fixture: 32 input records, 21 accepted, 11 quarantined. These are deliberately constructed demonstration counts, not measured client improvements.
- Repeated pipeline execution produces identical output bytes for identical inputs and leaves the raw CSVs unchanged. SHA-256 input fingerprints are recorded in the JSON report.
- Scenario outcomes: fictional South ranks first under Balanced and Low competition; fictional North ranks first under Access first. These differences arise from explicit, illustrative weights.
- Dashboard JavaScript syntax is checked with Node. Browser rendering and interactions still require a local manual check; a browser binary was unavailable in the preparation environment. The included SVG is a static data visualization, not an HTML screenshot.
- GEOTIP was reviewed at source level only. Arcade runtime, underlying service availability, permissions and the live dashboard were not tested.

Before publishing, the author should reproduce the examples locally, check the interactive scenario selector, make and explain original changes, and verify any links presented as live demonstrations.
