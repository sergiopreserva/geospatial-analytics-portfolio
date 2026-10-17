"""Reproducible portfolio demos. All bundled business/location data is synthetic."""
from __future__ import annotations

import argparse
import csv
import hashlib
from html import escape
import json
import math
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

AOI = (-74.25, 4.45, -73.95, 4.90)  # west, south, east, north; screening box only
CATEGORIES = {"retail", "transport", "service"}
SCENARIOS = {
    "Balanced": {"demand": 0.45, "access": 0.30, "competition": 0.25},
    "Access first": {"demand": 0.20, "access": 0.70, "competition": 0.10},
    "Low competition": {"demand": 0.25, "access": 0.20, "competition": 0.55},
}


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def number(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite number")
    return result


def in_aoi(lat: float, lon: float) -> bool:
    west, south, east, north = AOI
    return west <= lon <= east and south <= lat <= north


def read_csv(path: Path, required: set[str]) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"{path.name}: no data rows")
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError(f"{path.name}: malformed CSV row")
    return rows


def payload(row: dict) -> tuple:
    coords = []
    for key in ("latitude", "longitude"):
        try:
            coords.append(number(row[key].strip()))
        except ValueError:
            coords.append(normalize(row[key]))
    return (normalize(row["name"]).casefold(), normalize(row["category"]).casefold(), *coords)


def validate_locations(rows: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """Quarantine conflicting IDs, bad geometry and uncertain coordinates; never guess."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[normalize(row["source_id"]).upper()].append(payload(row))
    conflicts = {key for key, values in grouped.items() if key and len(set(values)) > 1}
    accepted, rejected, seen = [], [], set()
    for row_number, row in enumerate(rows, start=2):
        key = normalize(row["source_id"]).upper()
        name = normalize(row["name"])
        category = normalize(row["category"]).casefold()
        issues = []
        if not key:
            issues.append("missing_identifier")
        elif key in conflicts:
            issues.append("conflicting_identifier")
        elif key in seen:
            issues.append("duplicate_identifier")
        if key:
            seen.add(key)
        if not name:
            issues.append("missing_name")
        if category not in CATEGORIES:
            issues.append("unsupported_category")
        lat = lon = None
        try:
            lat, lon = number(row["latitude"]), number(row["longitude"])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                issues.append("invalid_coordinate_range")
            elif not in_aoi(lat, lon):
                issues.append("possible_swapped_coordinates" if in_aoi(lon, lat) else "outside_screening_box")
        except ValueError:
            issues.append("invalid_or_missing_coordinates")
        if issues:
            rejected.append({"source_row": row_number, **row, "issues": "|".join(issues)})
        else:
            accepted.append({"source_id": key, "name": name, "category": category,
                             "latitude": lat, "longitude": lon})
    reasons = Counter(issue for row in rejected for issue in row["issues"].split("|"))
    # Shared coordinates are review candidates, not proof of duplicate businesses.
    colocated = defaultdict(list)
    for row in accepted:
        colocated[(row["latitude"], row["longitude"])].append(row["source_id"])
    summary = {
        "input_rows": len(rows), "accepted_rows": len(accepted), "quarantined_rows": len(rejected),
        "acceptance_rate_pct": round(100 * len(accepted) / len(rows), 2),
        "issue_counts": dict(sorted(reasons.items())),
        "coincident_location_groups": [ids for ids in colocated.values() if len(ids) > 1],
        "rules": {"crs": "WGS84", "screening_box_wsen": AOI,
                  "coordinate_autocorrection": False, "conflicting_ids": "quarantine all versions"},
    }
    return accepted, rejected, summary


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371008.8 * 2 * math.atan2(math.sqrt(min(1, a)), math.sqrt(max(0, 1 - a)))


def screen_sites(candidates: list[dict], points: list[dict]) -> dict:
    transport = [row for row in points if row["category"] == "transport"]
    competitors = [row for row in points if row["category"] == "retail"]
    if not transport:
        raise ValueError("At least one accepted transport point is required")
    features, seen = [], set()
    for row in candidates:
        key = normalize(row["site_id"]).upper()
        if not key or key in seen:
            raise ValueError("Candidate site IDs must be non-empty and unique")
        seen.add(key)
        lat, lon = number(row["latitude"]), number(row["longitude"])
        demand = number(row["synthetic_demand_index"])
        if not in_aoi(lat, lon) or not 0 <= demand <= 100:
            raise ValueError(f"Invalid candidate: {key}")
        distance = min(haversine_m(lat, lon, p["latitude"], p["longitude"]) for p in transport)
        count = sum(haversine_m(lat, lon, p["latitude"], p["longitude"]) <= 500 for p in competitors)
        features.append({"site_id": key, "label": normalize(row["label"]),
                         "latitude": lat, "longitude": lon, "demand": demand,
                         "nearest_transport_m": distance, "competitors_500m": count,
                         "access": max(0, 100 * (1 - distance / 1500)),
                         "competition": 100 / (1 + count)})
    scenarios, top_counts = {}, Counter()
    for name, weights in SCENARIOS.items():
        ranked = [{**row, "score": sum(weights[k] * row[k] for k in weights)} for row in features]
        ranked.sort(key=lambda row: (-row["score"], row["site_id"]))
        for rank, row in enumerate(ranked, start=1):
            row["rank"] = rank
        scenarios[name] = {"weights": weights, "ranking": ranked}
        top_counts[ranked[0]["site_id"]] += 1
    return {"scenarios": scenarios, "top_rank_count": dict(top_counts),
            "candidate_count": len(features), "distance_method": "great-circle haversine, metres",
            "disclaimer": "Synthetic heuristic screening; not observed foot traffic, revenue or a causal model."}


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def preview_svg(report: dict) -> str:
    """A data-driven static overview, not a screenshot of the HTML interface."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="770" viewBox="0 0 1200 770">',
             '<rect width="1200" height="770" fill="#f4f2ec"/>',
             '<rect width="1200" height="145" fill="#142d3b"/>']
    def text(x, y, value, size=18, fill="#183040", weight="normal"):
        parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" '
                     f'fill="{fill}" font-weight="{weight}">{escape(str(value))}</text>')
    text(40, 37, "SYNTHETIC DATA / PORTFOLIO DEMONSTRATION", 14, "#ffbf76", "bold")
    text(40, 86, "From location records to a defensible shortlist.", 35, "#ffffff", "bold")
    text(40, 120, "A static overview generated from the same Python outputs as the interactive dashboard.", 17, "#c7d6da")
    quality = report["quality"]
    for x, title, value in [(40, "INPUT RECORDS", quality["input_rows"]),
                             (420, "ACCEPTED", quality["accepted_rows"]),
                             (800, "QUARANTINED", quality["quarantined_rows"])]:
        parts.append(f'<rect x="{x}" y="170" width="360" height="115" rx="12" fill="#ffffff"/>')
        text(x + 24, 202, title, 14, "#50666d", "bold")
        text(x + 24, 254, value, 40, "#183040", "bold")
    parts.extend(['<rect x="40" y="310" width="620" height="330" rx="12" fill="#ffffff"/>',
                  '<rect x="680" y="310" width="480" height="330" rx="12" fill="#ffffff"/>'])
    text(65, 350, "Balanced scenario", 23, weight="bold")
    text(65, 380, "Demand 45% / Access 30% / Competition 25%", 15, "#50666d")
    ranking = report["screening"]["scenarios"]["Balanced"]["ranking"]
    for index, row in enumerate(ranking):
        y = 420 + index * 49
        text(65, y + 16, row["site_id"], 18, weight="bold")
        parts.append(f'<rect x="100" y="{y}" width="425" height="21" rx="4" fill="#e9eeec"/>')
        parts.append(f'<rect x="100" y="{y}" width="{row["score"] * 4.25:.2f}" height="21" rx="4" fill="#1c777b"/>')
        text(545, y + 17, f'{row["score"]:.1f}/100', 17, weight="bold")
    text(705, 350, "Which site ranks first?", 23, weight="bold")
    for index, (name, result) in enumerate(report["screening"]["scenarios"].items()):
        y = 398 + index * 75
        text(705, y, name, 16, "#50666d")
        text(705, y + 28, result["ranking"][0]["label"], 22, weight="bold")
    text(40, 682, "Decision: shortlist for investigation; validate actual demand, rents and travel times before investing.", 18, weight="bold")
    text(40, 718, "All businesses, point locations and demand values are invented. Scores are heuristics, not revenue predictions.", 16, "#50666d")
    text(40, 746, "Straight-line distances / no observed foot traffic / no causal claims / no Placer.ai data", 15, "#50666d")
    return "\n".join([*parts, "</svg>"]) + "\n"


def run(root: Path) -> dict:
    data, output = root / "data", root / "outputs"
    output.mkdir(exist_ok=True)
    raw_path, site_path = data / "locations_raw.csv", data / "candidate_sites.csv"
    raw = read_csv(raw_path, {"source_id", "name", "category", "latitude", "longitude"})
    sites = read_csv(site_path, {"site_id", "label", "latitude", "longitude", "synthetic_demand_index"})
    accepted, rejected, quality = validate_locations(raw)
    screening = screen_sites(sites, accepted)
    provenance = {"data_type": "synthetic", "source_sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (raw_path, site_path)}}
    report = {"provenance": provenance, "quality": quality, "screening": screening, "locations": accepted}
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "results-preview.svg").write_text(preview_svg(report), encoding="utf-8")
    write_csv(output / "accepted_locations.csv", accepted,
              ["source_id", "name", "category", "latitude", "longitude"])
    write_csv(output / "quarantined_locations.csv", rejected, ["source_row", *raw[0], "issues"])
    flat = [{"scenario": name, **row} for name, result in screening["scenarios"].items() for row in result["ranking"]]
    write_csv(output / "site_ranking.csv", flat, list(flat[0]))
    geojson = {"type": "FeatureCollection", "features": [{"type": "Feature",
        "geometry": {"type": "Point", "coordinates": [p["longitude"], p["latitude"]]},
        "properties": {key: value for key, value in p.items() if key not in {"longitude", "latitude"}}}
        for p in accepted]}
    for name, payload_data in (("report.json", report), ("accepted_locations.geojson", geojson)):
        (output / name).write_text(json.dumps(payload_data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    template = (root / "src" / "dashboard.html").read_text(encoding="utf-8")
    safe_json = json.dumps(report, allow_nan=False).replace("<", "\\u003c")
    (output / "dashboard.html").write_text(template.replace("__REPORT_JSON__", safe_json), encoding="utf-8")
    balanced = screening["scenarios"]["Balanced"]["ranking"]
    recommendation = (
        "# Screening brief — synthetic demonstration\n\n"
        f"The balanced scenario ranks **{balanced[0]['label']} ({balanced[0]['site_id']})** first "
        f"with a score of **{balanced[0]['score']:.1f}/100**. This is a relative heuristic score, not a probability.\n\n"
        f"Quality gate: {quality['accepted_rows']} of {quality['input_rows']} records accepted; "
        f"{quality['quarantined_rows']} quarantined with explicit reasons. Input files were not modified.\n\n"
        "## Sensitivity\n\n"
        + "\n".join(f"- {name}: {result['ranking'][0]['site_id']} ranks first."
                    for name, result in screening["scenarios"].items())
        + "\n\n## Decision\n\nShortlist locations for further investigation rather than committing to a lease. "
        "Validate real demand, point-of-interest completeness, travel times, rents and unit economics first. "
        "The three weight settings are illustrative assumptions, not stakeholder-elicited preferences or confidence intervals.\n\n"
        "## Limits\n\nAll locations and demand values are fictional. The rectangular extent is a screening box, "
        "not the Bogotá municipal boundary. Distances are straight-line great-circle distances, not walking or driving distances. "
        "Fewer nearby competitors is an explicit model assumption; clustering may also signal stronger demand. "
        "No external truth dataset was used to verify the synthetic coordinates.\n"
    )
    (output / "screening_brief.md").write_text(recommendation, encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    result = run(parser.parse_args().root)
    print(json.dumps({"quality": result["quality"],
                      "top_rank_count": result["screening"]["top_rank_count"]}, indent=2))
