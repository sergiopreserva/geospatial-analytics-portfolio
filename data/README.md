# Data provenance and dictionary

The two CSV files were authored for this portfolio demonstration on 17 October 2026. Every business label, coordinate and demand value is synthetic. Geographic context is an approximate Bogotá-area rectangle, not an authoritative Bogotá boundary. No geocoding service, Placer.ai API, mobility dataset, company client record or proprietary business data was used.

`locations_raw.csv` intentionally contains invalid records for the quality gate. It is not a record of data defects in any real organization.

| File / field | Meaning |
|---|---|
| locations / source_id | Fictional business key; conflicting versions require review |
| locations / name | Invented feature name |
| locations / category | retail, transport or service; retail is treated as a competitor proxy |
| latitude, longitude | Synthetic WGS84 decimal degrees, explicitly separate columns |
| candidates / site_id, label | Fictional candidate identifier and label |
| candidates / synthetic_demand_index | Invented 0–100 scenario input, not an observed or validated demand metric |

GeoJSON output uses `[longitude, latitude]`. Distance calculations use a spherical great-circle approximation and return metres. A shared coordinate is not automatically a duplicate. No personal data or device-level observations are included.

Outputs include SHA-256 input fingerprints. If replacing the bundled files, update this provenance statement and review the spatial extent, schema, categories and model assumptions before interpreting results.
