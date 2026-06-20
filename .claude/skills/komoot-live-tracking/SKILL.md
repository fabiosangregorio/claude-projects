---
name: komoot-live-tracking
description: Coach a live outdoor activity from a Komoot live tracking link. Use when the user shares a komoot.com/live URL, invokes /komoot-live-tracking, asks for live position checks, asks how much remains, compares a route to Brenta training, or wants live pacing/fueling/heat/safety guidance.
---

# Komoot live tracking coach

Use this skill when the user wants live help from a Komoot live tracking link. The core pattern is:

**live Komoot point -> planned Komoot route coordinates -> nearest route position -> route remaining/profile -> coaching advice.**

Komoot's public pages can expose partial or inconsistent fields. Treat the live page as a source of current GPS coordinates, not as a complete activity API.

## Inputs

- A `https://www.komoot.com/live/...` URL.
- Optionally a planned tour URL or ID, usually present in the live page as `https://www.komoot.com/tour/<tour_id>`.
- Optional athlete context from this workspace:
  - `trail-brenta-2026/data/plan.json`
  - `trail-brenta-2026/data/weeks/*.json`
  - `trail-brenta-2026/data/race.json`
  - `trail-brenta-2026/data/profile.json`

## Tools and endpoints

### 1. Read the live page

Fetch the live URL. Extract:

- current or last location: `lat,lng`
- location accuracy
- last update age
- activity status
- planned tour link, if present

Do **not** rely on:

- `Elapsed time` when it conflicts with user report
- `-- yd remaining`
- the rendered elevation profile; it is usually not exposed numerically by the fetched HTML

If the fetch times out, retry once before falling back to the last known live point.

### 2. Read the planned Komoot tour

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

### 3. Read full planned coordinates

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

### 5. Optional reverse geocoding/elevation fallback

Only if planned coordinates are unavailable or clearly stale:

- use Open-Elevation for approximate altitude from live `lat,lng`
- use Nominatim/OpenStreetMap reverse geocoding for locality/road names

When planned coordinates are available, prefer Komoot route altitudes over external elevation APIs because they align with the planned profile.

## Route matching workflow

1. Refresh live URL and get current `lat,lng`.
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

## Coaching output style

The user may be moving, tired, hot, or stressed. Keep live responses short and operational.

For each live check, prefer:

1. where they are on the route
2. what comes next
3. one immediate instruction
4. one safety check if conditions are harsh

Example:

```text
Sei circa al km 5.8 della traccia, quota ~910 m. Prossimi 600-800 m ancora ripidi, poi molla un po'. Adesso cammina forte: passo corto, mani sulle cosce, niente acido.
```

## Training-plan integration for Brenta

When the user asks about XTERRA Dolomiti di Brenta / "Brenta":

1. Read `trail-brenta-2026/data/race.json`.
2. Read current week from `trail-brenta-2026/data/weeks/index.json` and the latest week file.
3. Read `trail-brenta-2026/data/plan.json` for phase rules.
4. Compare the live activity against the plan conservatively.

Known Brenta references from the plan:

- race: XTERRA Dolomiti di Brenta Trail SHORT 21K
- race distance: 21 km
- race D+: 1250 m
- cutoff: Rifugio Croz dell'Altissimo within 3h
- grade distribution reference:
  - ~24% steep uphill >10%
  - ~26% steep downhill >10%
- current plan may include injury constraints; never ignore active rehab notes

If the current week says D+ is suspended or the hip is being protected, say so plainly and shift advice toward damage control:

- hike steep climbs
- run only easy traverses/flats
- descend conservatively
- prioritize the 24h pain response over today's pace

## Fueling and heat guidance

For hard mountain efforts:

- caffeine gel: usually useful before or early in the hard section, with water, not when already nauseous or overheated
- water-only intake in heat can still leave sodium deficit; suggest salty food/sports drink after
- if the user reports heat stress, stop coaching for pace and coach cooling:
  - walk
  - shade
  - small sips
  - wet head/neck/wrists if possible
  - seek help if red flags appear

Heat red flags:

- confusion
- faintness or inability to walk straight
- vomiting
- chills/goosebumps in heat
- severe or worsening headache
- chest pain
- stopped sweating while feeling hot

Tell the user to stop, contact someone nearby, or call emergency services if these appear.

## Known sharp edges

- The live page is not a streaming API. You must refresh/fetch it for each check.
- Komoot may show `Last Location` rather than `Current location`; either can be used if recent.
- `Elapsed time` can be wrong or reset in the public page. Trust user report and GPS progression over that field.
- Planned tour coordinates are not the recorded live track. If the athlete deviates, nearest-point estimates become uncertain.
- The public tour endpoint may be reachable even when the GPX endpoint is not.
- External elevation APIs may disagree with Komoot altitudes; do not mix them silently.
- Do not provide medical diagnosis. Give conservative safety guidance and escalation criteria.

## When to stop using this skill

- The activity is finished and the user asks for post-run analysis; switch to normal activity-analysis workflow.
- The user asks to log the activity into the training plan; use the repository's activity logging conventions instead.
- The user reports emergency symptoms; prioritize emergency guidance over route analysis.
