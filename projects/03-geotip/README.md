# GEOTIP · Arcade Expressions for Earthquake Dashboards

**Type:** existing public source; newly written case-study draft. Live dashboard operation has not been verified in this portfolio preparation.

[Original repository](https://github.com/sergiopreserva/dashboards-codigos-geotip)

## Problem and evidence

The existing repository contains Arcade expressions for querying ArcGIS Online features and preparing earthquake data for ArcGIS Dashboards: ranking records by magnitude or event time and summarizing spatial matches against country polygons.

The source demonstrates use of `FeatureSetByPortalItem`, filtering, ordering, output FeatureSet construction and spatial intersection. It requests geometry where spatial operations need it and omits geometry from simple record listings.

## Source reviewed

Review snapshot: commit `2ef5e70c2be327c4a80d3a63ebeb1f7c1e56aedc` on 17 October 2026. This portfolio links to the original source without changing or relicensing it.

- [Repository README](https://github.com/sergiopreserva/dashboards-codigos-geotip/blob/2ef5e70c2be327c4a80d3a63ebeb1f7c1e56aedc/README.md).
- [Country intersection expression](https://github.com/sergiopreserva/dashboards-codigos-geotip/blob/2ef5e70c2be327c4a80d3a63ebeb1f7c1e56aedc/expresion_interseccion_espacial).
- [Magnitude-ranking example](https://github.com/sergiopreserva/dashboards-codigos-geotip/blob/2ef5e70c2be327c4a80d3a63ebeb1f7c1e56aedc/expresiones-columna-derecha/segundo_registro_de_mayor_magnitud).

## Technical review: what must be explained before presenting

1. **Scope of the country summary.** The expression filters magnitude ≥4 and age ≤168 hours, then takes only the 100 most recent records before aggregation. Its top countries describe that capped subset, not necessarily all matching events in the seven-day period. It must be labeled accordingly or the aggregation must be redesigned.
2. **Unmatched events.** Offshore or otherwise unmatched points are excluded from the country output. A production report should reconcile matched and unmatched counts rather than implying full coverage.
3. **Ambiguous matches.** Selecting `First` from intersecting country polygons does not establish an explicit boundary/overlap policy.
4. **Ranking ties.** Ordering only by magnitude does not define a unique total order for equal magnitudes. A secondary key and an explicit tie policy are needed if exactly one event per rank is required.
5. **Documentation.** The original README has an unclosed code fence and names a `.arcade` filename that differs from the actual file. Some magnitude-ranking comments describe time ordering. These are documentation defects, not evidence that the runtime failed.

No live-service validation, runtime benchmark or performance improvement is claimed. Suggested changes above have not been deployed.

## Portfolio completion

Add an approved screenshot or public dashboard link, a short statement of personal contribution, and the observed query window and refresh behavior. Until that evidence is verified, present this as a code case study rather than a validated live demo.
