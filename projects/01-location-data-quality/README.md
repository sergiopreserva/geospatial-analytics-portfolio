# Location Data Quality

**Type:** new synthetic demonstration, AI-assisted draft for author review.

## Problem

A location analysis is only as useful as its underlying records. Missing coordinates, conflicting identifiers and silent axis swaps can place the wrong locations on a map and distort a business decision.

## Approach

The Python quality gate reads an immutable CSV and checks identifiers, required fields, categories, finite coordinates, global ranges and a rectangular screening extent. Exact repeated identifiers keep one canonical record. Conflicting versions of an identifier are all quarantined for review. Possible latitude/longitude swaps are flagged and never automatically corrected.

Distinct businesses at the same coordinates remain valid records, with a separate co-location review flag. A shared point can represent a mall or a shared entrance and is not sufficient evidence of a duplicate business.

## Evidence

- [Implementation](../../src/portfolio.py): `validate_locations`.
- [Original input](../../data/locations_raw.csv).
- [Accepted records](../../outputs/accepted_locations.csv).
- [Quarantine log](../../outputs/quarantined_locations.csv).
- [Quality counts and source hashes](../../outputs/report.json).
- [ArcGIS-compatible GeoJSON](../../outputs/accepted_locations.geojson), with longitude before latitude.

Run from the repository root: `python src/portfolio.py`.

## Interpretation

Acceptance means passing documented screening rules. It does not prove that a business exists or that its coordinates are correct. This exercise deliberately uses synthetic data and therefore cannot demonstrate cross-validation against an external ground-truth source.

## Next extension

Replace the rectangle with an authoritative administrative boundary; add a licensed reference dataset and address matching; retain uncertain matches for manual review. Those extensions are not implemented in this version.
