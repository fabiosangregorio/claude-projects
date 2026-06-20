---
name: komoot-live-tracking
description: Extract live tracking state from a Komoot live URL. Use when the user shares a komoot.com/live link, invokes /komoot-live-tracking, asks whether the live link is accessible, wants the current position, or needs route progress/distance/elevation estimates from Komoot data.
---

# Komoot live tracking

Use this skill to turn a Komoot live tracking link into structured tracking data.

Core pattern:

```text
live Komoot point -> planned Komoot route coordinates -> nearest route position -> route progress/profile
```

Komoot's public pages can expose partial or inconsistent fields. Treat the live page as a source of current GPS coordinates, not as a complete activity API.

This skill is intentionally limited to tracking extraction and route math. Do not interpret the data into athlete guidance or activity decisions.

## Inputs

- A `https://www.komoot.com/live/...` URL.
- Optionally a planned tour URL or ID, usually present in the live page as `https://www.komoot.com/tour/<tour_id>`.

## Output contract

Return the most useful subset of this state:

```json
{
  "activity_status": "Active",
  "live_point": {
    "lat": 45.744646,
    "lng": 9.662524,
    "accuracy": "5 yd",
    "last_update": "less than a minute ago",
    "source_label": "Current location"
  },
  "tour": {
    "id": "3050332229",
    "name": "da Sorisole a Canto Alto",
    "distance_m": 11547.6,
    "elevation_up_m": 733.2,
    "elevation_down_m": 733.2
  },
  "route_match": {
    "matched": true,
    "confidence": "good",
    "nearest_distance_m": 12,
    "route_index": 123,
    "distance_done_m": 5400,
    "distance_remaining_m": 6150,
    "elevation_up_remaining_m": 320,
    "elevation_down_remaining_m": 690,
    "planned_altitude_m": 843
  },
  "next_profile": {
    "window_m": 300,
    "grade_pct": 14,
    "elevation_delta_m": 42
  },
  "warnings": []
}
```

If a field is unknown, omit it or add a short warning. Do not invent exact values.

## Endpoints

### 1. Live page

Fetch the live URL. Extract:

- current or last location: `lat,lng`
- location accuracy
- last update age
- activity status
- planned tour link, if present

Do not rely on:

- `Elapsed time` when it conflicts with user report
- `-- yd remaining`
- the rendered elevation profile; it is usually not exposed numerically by the fetched HTML

If the fetch times out, retry once before falling back to the last known live point.

### 2. Planned tour metadata

If the live page includes a tour URL, fetch:

```text
https://www.komoot.com/api/v007/tours/<tour_id>
```

Useful fields:

- `distance`
- `duration`
- `elevation_up`
- `elevation_down`
- `start_point`
- `path` rough shape
- `_links.coordinates.href`
- `_links.tour_line.href`
- `tour_information` danger/technical segments
- `summary.surfaces`
- `summary.way_types`

### 3. Full planned coordinates

Fetch:

```text
https://api.komoot.de/v007/tours/<tour_id>/coordinates
```

This returns the planned route as JSON:

```json
{
  "items": [
    { "lat": 45.744646, "lng": 9.662524, "alt": 407.3, "t": 0 }
  ]
}
```

This is not GPX, but it is effectively the planned track and can be converted to GPX if needed. Use it directly for route matching.

Alternative:

```text
https://api.komoot.de/v007/tours/<tour_id>/tour_line
```

This returns a `geometry` array with `lat`, `lng`, and `alt`.

### 4. GPX direct download

Do not assume GPX is publicly available. A URL such as:

```text
https://www.komoot.com/api/v007/tours/<tour_id>.gpx
```

may fail with `503 Service Unavailable` or require non-public access. Prefer `/coordinates`.

### 5. Optional fallback data

Only if planned coordinates are unavailable or clearly stale:

- use Open-Elevation for approximate altitude from live `lat,lng`
- use Nominatim/OpenStreetMap reverse geocoding for locality/road names

When planned coordinates are available, prefer Komoot route altitudes over external elevation APIs because they align with the planned profile.

## Workflow

1. Refresh the live URL and get current `lat,lng`.
2. Fetch planned coordinates once, cache mentally for the conversation, and reuse unless the tour ID changes.
3. Find the nearest route point to the live point using haversine distance.
4. Reject the match or state uncertainty if nearest distance is large:
   - `<30 m`: good match
   - `30-80 m`: usable but mention slight uncertainty
   - `>80 m`: likely off-route, shortcut, GPS drift, or different route; avoid precise remaining-distance claims
5. Compute cumulative route distance and D+/D- from planned coordinates.
6. From nearest index, estimate:
   - distance already covered on planned route
   - distance remaining
   - D+ remaining
   - D- remaining
   - current planned altitude
   - next segment profile
7. For current/next grade, use a short window, e.g. 100-300 m ahead:
   - grade = elevation_delta / horizontal_distance
   - report as a range, not false precision

## Route math

### Haversine distance

Use haversine distance for point-to-point route matching. A rough local approximation is acceptable for short windows, but do not use raw degree deltas as meters.

### Cumulative distance

For the coordinate list:

1. compute distance between consecutive points
2. store cumulative distance at every index
3. `distance_done_m = cumulative[index]`
4. `distance_remaining_m = total_distance - cumulative[index]`

### Cumulative elevation

From planned coordinate altitudes:

1. for every consecutive point pair, compute `delta_alt`
2. add positive deltas to cumulative D+
3. add absolute negative deltas to cumulative D-
4. compute remaining D+/D- from the matched index to the end

Use Komoot's own `elevation_up`/`elevation_down` as the top-level route totals when available. Use point-derived elevation only for local/remaining estimates.

### Next profile window

To describe the route ahead:

1. choose a distance window, usually 100-300 m for live use
2. find the coordinate index at `current_cumulative + window_m`
3. compute horizontal distance and altitude delta between current and target index
4. compute grade percentage

If the window contains switchbacks or mixed terrain, report a range or say the profile is mixed.

## Response style

Keep responses data-first and neutral. Examples:

```text
Live point: 45.76025, 9.67610, updated less than a minute ago.
Matched to planned route with good confidence, about 5.6 km in. Estimated remaining: 5.9 km, +250 m / -720 m. Next 300 m: steep, roughly +40 m.
```

```text
I can access the live link, but I cannot match the point confidently to the planned route: nearest route point is about 140 m away. Current live point is 45.75082, 9.66130.
```

Do not append action instructions such as when to run, what to eat, or how to manage physical risk. A separate higher-level skill should consume this tracking state if the user asks for guidance.

## Known sharp edges

- The live page is not a streaming API. You must refresh/fetch it for each check.
- Komoot may show `Last Location` rather than `Current location`; either can be used if recent.
- `Elapsed time` can be wrong or reset in the public page. Trust user report and GPS progression over that field.
- Planned tour coordinates are not the recorded live track. If the athlete deviates, nearest-point estimates become uncertain.
- The public tour endpoint may be reachable even when the GPX endpoint is not.
- External elevation APIs may disagree with Komoot altitudes; do not mix them silently.

## When not to use this skill

- The user asks what to do next based on the tracking data. Use a separate higher-level skill.
- The activity is finished and the user asks for post-run analysis. Use the normal activity-analysis workflow.
- The user asks to log the activity into the training plan. Use the repository's activity logging conventions instead.
