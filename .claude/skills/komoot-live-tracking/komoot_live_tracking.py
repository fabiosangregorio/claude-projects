#!/usr/bin/env python3
"""Extract structured state from a public Komoot live tracking URL.

The script intentionally stays limited to data extraction and route math:
live point, planned tour metadata, nearest point on planned route, remaining
distance/elevation, and a short route-profile window.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = "komoot-live-tracking-skill/1.0"
DEFAULT_WINDOW_M = 300.0
GOOD_MATCH_M = 30.0
USABLE_MATCH_M = 80.0


class TrackingError(RuntimeError):
    """Raised when required tracking data cannot be extracted."""


@dataclass(frozen=True)
class RoutePoint:
    lat: float
    lng: float
    alt: float | None = None


def fetch_text(url: str, timeout: float, retries: int) -> str:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset, errors="replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise TrackingError(f"Failed to fetch {url}: {last_error}")


def fetch_json(url: str, timeout: float, retries: int) -> dict[str, Any]:
    text = fetch_text(url, timeout=timeout, retries=retries)
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TrackingError(f"Expected JSON from {url}: {exc}") from exc
    if not isinstance(data, dict):
        raise TrackingError(f"Expected JSON object from {url}")
    return data


def text_from_html(raw: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_live_state(raw: str) -> dict[str, Any]:
    text = text_from_html(raw)
    state: dict[str, Any] = {}

    status_match = re.search(r"Activity status\s*:\s*([A-Za-z]+)", text, re.I)
    if status_match:
        state["activity_status"] = status_match.group(1)

    point_patterns = [
        ("Current location", r"Current location\s*:\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)"),
        ("Last Location", r"Last Location\s*:\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)"),
        ("Last location", r"Last location\s*:\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)"),
    ]
    for label, pattern in point_patterns:
        point_match = re.search(pattern, text, re.I)
        if point_match:
            state["live_point"] = {
                "lat": float(point_match.group(1)),
                "lng": float(point_match.group(2)),
                "source_label": label,
            }
            break

    if "live_point" in state:
        accuracy_match = re.search(r"Location accuracy\s*:\s*([^\s]+(?:\s+(?:yd|m|ft))?)", text, re.I)
        if accuracy_match:
            state["live_point"]["accuracy"] = accuracy_match.group(1)
        update_match = re.search(
            r"Last update\s*:\s*(.*?)(?=\s+(?:Saved route|Recorded route|ELEVATION PROFILE|ROUTE INFO|Have questions|$))",
            text,
            re.I,
        )
        if update_match:
            state["live_point"]["last_update"] = update_match.group(1).strip()

    tour_match = re.search(r"(?:https://(?:www\.)?komoot\.com)?/tour/(\d+)", raw)
    if tour_match:
        state["tour_id"] = tour_match.group(1)

    return state


def extract_tour_id(value: str) -> str | None:
    if value.isdigit():
        return value
    match = re.search(r"komoot\.com/tour/(\d+)", value)
    if match:
        return match.group(1)
    return None


def tour_metadata(tour: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for source, target in [
        ("id", "id"),
        ("name", "name"),
        ("distance", "distance_m"),
        ("duration", "duration_s"),
        ("elevation_up", "elevation_up_m"),
        ("elevation_down", "elevation_down_m"),
        ("sport", "sport"),
    ]:
        if source in tour and tour[source] is not None:
            result[target] = tour[source]
    return result


def parse_route_points(payload: dict[str, Any]) -> list[RoutePoint]:
    raw_points = payload.get("items") or payload.get("geometry")
    if not isinstance(raw_points, list):
        raise TrackingError("Coordinates payload does not contain items or geometry")

    points: list[RoutePoint] = []
    for raw in raw_points:
        if not isinstance(raw, dict):
            continue
        lat = raw.get("lat")
        lng = raw.get("lng")
        alt = raw.get("alt")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            points.append(RoutePoint(float(lat), float(lng), float(alt) if isinstance(alt, (int, float)) else None))

    if len(points) < 2:
        raise TrackingError("Coordinates payload contains fewer than two usable points")
    return points


def haversine_m(a: RoutePoint, b: RoutePoint) -> float:
    radius_m = 6_371_000.0
    lat1 = math.radians(a.lat)
    lat2 = math.radians(b.lat)
    d_lat = math.radians(b.lat - a.lat)
    d_lng = math.radians(b.lng - a.lng)
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return 2 * radius_m * math.asin(math.sqrt(h))


def cumulative_distance(points: list[RoutePoint]) -> list[float]:
    values = [0.0]
    for previous, current in zip(points, points[1:]):
        values.append(values[-1] + haversine_m(previous, current))
    return values


def cumulative_elevation(points: list[RoutePoint]) -> tuple[list[float], list[float]]:
    up = [0.0]
    down = [0.0]
    for previous, current in zip(points, points[1:]):
        delta = None if previous.alt is None or current.alt is None else current.alt - previous.alt
        up.append(up[-1] + (delta if delta is not None and delta > 0 else 0.0))
        down.append(down[-1] + (-delta if delta is not None and delta < 0 else 0.0))
    return up, down


def nearest_index(points: list[RoutePoint], live_point: RoutePoint) -> tuple[int, float]:
    best_index = 0
    best_distance = float("inf")
    for index, point in enumerate(points):
        distance = haversine_m(live_point, point)
        if distance < best_distance:
            best_index = index
            best_distance = distance
    return best_index, best_distance


def confidence(distance_m: float) -> str:
    if distance_m < GOOD_MATCH_M:
        return "good"
    if distance_m <= USABLE_MATCH_M:
        return "usable"
    return "poor"


def index_at_distance(cumulative: list[float], target_m: float, start_index: int) -> int:
    for index in range(start_index, len(cumulative)):
        if cumulative[index] >= target_m:
            return index
    return len(cumulative) - 1


def route_match(points: list[RoutePoint], live: RoutePoint, window_m: float) -> tuple[dict[str, Any], dict[str, Any] | None]:
    distances = cumulative_distance(points)
    elevation_up, elevation_down = cumulative_elevation(points)
    index, nearest_distance = nearest_index(points, live)
    match_confidence = confidence(nearest_distance)

    total_distance = distances[-1]
    match: dict[str, Any] = {
        "matched": match_confidence != "poor",
        "confidence": match_confidence,
        "nearest_distance_m": round(nearest_distance, 1),
        "route_index": index,
        "distance_done_m": round(distances[index], 1),
        "distance_remaining_m": round(max(0.0, total_distance - distances[index]), 1),
        "elevation_up_remaining_m": round(max(0.0, elevation_up[-1] - elevation_up[index]), 1),
        "elevation_down_remaining_m": round(max(0.0, elevation_down[-1] - elevation_down[index]), 1),
    }
    if points[index].alt is not None:
        match["planned_altitude_m"] = round(points[index].alt, 1)

    profile = None
    if index < len(points) - 1 and total_distance > distances[index]:
        target_index = index_at_distance(distances, min(total_distance, distances[index] + window_m), index)
        horizontal_m = distances[target_index] - distances[index]
        start_alt = points[index].alt
        end_alt = points[target_index].alt
        if horizontal_m > 0 and start_alt is not None and end_alt is not None:
            delta = end_alt - start_alt
            profile = {
                "window_m": round(horizontal_m, 1),
                "grade_pct": round((delta / horizontal_m) * 100, 1),
                "elevation_delta_m": round(delta, 1),
            }

    return match, profile


def coordinates_url(tour: dict[str, Any], tour_id: str) -> str:
    links = tour.get("_links")
    if isinstance(links, dict):
        coordinates = links.get("coordinates")
        if isinstance(coordinates, dict) and isinstance(coordinates.get("href"), str):
            return coordinates["href"].replace("https://api.komoot.de", "https://api.komoot.de")
    return f"https://api.komoot.de/v007/tours/{tour_id}/coordinates"


def tour_line_url(tour: dict[str, Any], tour_id: str) -> str:
    links = tour.get("_links")
    if isinstance(links, dict):
        tour_line = links.get("tour_line")
        if isinstance(tour_line, dict) and isinstance(tour_line.get("href"), str):
            return tour_line["href"]
    return f"https://api.komoot.de/v007/tours/{tour_id}/tour_line"


def build_state(args: argparse.Namespace) -> dict[str, Any]:
    warnings: list[str] = []
    live_raw = fetch_text(args.live_url, timeout=args.timeout, retries=args.retries)
    live_state = extract_live_state(live_raw)

    state: dict[str, Any] = {}
    if "activity_status" in live_state:
        state["activity_status"] = live_state["activity_status"]

    live_point_data = live_state.get("live_point")
    if not isinstance(live_point_data, dict):
        raise TrackingError("Could not extract live coordinates from Komoot live page")
    state["live_point"] = live_point_data
    live_point = RoutePoint(float(live_point_data["lat"]), float(live_point_data["lng"]))

    tour_id = args.tour_id or live_state.get("tour_id")
    if tour_id:
        parsed_tour_id = extract_tour_id(str(tour_id))
        if not parsed_tour_id:
            warnings.append(f"Could not parse tour id from {tour_id}")
            tour_id = None
        else:
            tour_id = parsed_tour_id

    if tour_id:
        try:
            tour = fetch_json(f"https://api.komoot.de/v007/tours/{tour_id}", timeout=args.timeout, retries=args.retries)
        except TrackingError as exc:
            warnings.append(str(exc))
            state["warnings"] = warnings
            return state

        state["tour"] = tour_metadata(tour)
        points: list[RoutePoint] | None = None
        try:
            points = parse_route_points(fetch_json(coordinates_url(tour, tour_id), timeout=args.timeout, retries=args.retries))
        except TrackingError as exc:
            warnings.append(str(exc))
            try:
                points = parse_route_points(fetch_json(tour_line_url(tour, tour_id), timeout=args.timeout, retries=args.retries))
            except TrackingError as fallback_exc:
                warnings.append(str(fallback_exc))

        if points:
            match, profile = route_match(points, live_point, args.window_m)
            state["route_match"] = match
            if profile:
                state["next_profile"] = profile
            if match["confidence"] == "poor":
                warnings.append("Live point is far from the planned route; route-progress estimates may be unreliable")
    else:
        warnings.append("No planned tour id found; returning live point only")

    state["warnings"] = warnings
    return state


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract structured state from a Komoot live tracking URL.")
    parser.add_argument("live_url", help="Komoot live tracking URL")
    parser.add_argument("--tour-id", help="Komoot planned tour id or tour URL. Defaults to the tour linked from the live page.")
    parser.add_argument("--window-m", type=float, default=DEFAULT_WINDOW_M, help="Distance window for next-profile estimate.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds.")
    parser.add_argument("--retries", type=int, default=1, help="Number of retries per request.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        state = build_state(args)
    except TrackingError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    indent = None if args.compact else 2
    print(json.dumps(state, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
