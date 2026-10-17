# Transparent Location Screening

**Type:** new synthetic demonstration, AI-assisted draft for author review.

## Business question

Which of four fictional sites should receive further investigation, and does that shortlist change when decision-makers prioritize access or fewer nearby competitors?

## Method

Only records that pass Project 1 enter this analysis. The script calculates the nearest fictional transport access point and the number of accepted retail points within 500 metres, using great-circle distances.

Three scores range from 0 to 100:

- **Demand:** a supplied synthetic index; it is not estimated from real visits or population.
- **Access:** `max(0, 100 × (1 − nearest_access_metres / 1500))`.
- **Competition:** `100 / (1 + competitor_count_within_500m)`.

The final score is a weighted sum. Balanced weights are 45% demand, 30% access and 25% competition. Two additional scenarios change those priorities. Equal scores are ordered by site ID for deterministic output; that tie-break is not a business preference.

These are illustrative assumptions, not calibrated weights. No statistical significance or causal effect is claimed. Fewer competitors may signal whitespace or insufficient demand; the model assumes the former only for demonstration.

## Deliverables

- [Candidate inputs](../../data/candidate_sites.csv).
- [Calculation code](../../src/portfolio.py): `haversine_m` and `screen_sites`.
- [All scenario rankings](../../outputs/site_ranking.csv).
- [Client-style screening brief](../../outputs/screening_brief.md).
- [Interactive HTML dashboard](../../outputs/dashboard.html), with precomputed scenarios.

## Decision and limits

The result supports a shortlist, not an investment decision. The candidate with the highest score is not necessarily the most profitable site. Straight-line distances do not account for walking routes, road barriers or public-transport service. A real study needs observed demand, complete reference data, rents, operational constraints and field checks.

## Next extension

Implement a comparable report in Power BI or Tableau, with a documented data model and a real public dataset. The current custom HTML dashboard does not demonstrate proficiency in those products.
