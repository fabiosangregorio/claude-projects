---
name: komoot-live-tracking
description: Extract live tracking state from a Komoot live URL. Use when the user shares a komoot.com/live link, invokes /komoot-live-tracking, asks whether the live link is accessible, wants the current position, or needs route progress/distance/elevation estimates from Komoot data.
---

# Komoot live tracking

Use this skill to turn a Komoot live tracking link into structured tracking data.

This skill is intentionally limited to tracking extraction and route math. Do not interpret the data into athlete guidance or activity decisions.

## Run the helper script

Use the bundled helper as the source of truth:

```bash
python3 /workspace/.claude/skills/komoot-live-tracking/komoot_live_tracking.py '<komoot-live-url>'
```

If the live page does not expose the planned tour ID, pass it explicitly:

```bash
python3 /workspace/.claude/skills/komoot-live-tracking/komoot_live_tracking.py '<komoot-live-url>' --tour-id '<tour-id-or-tour-url>'
```

Useful options:

- `--window-m 300` — distance window for the next-profile estimate
- `--timeout 15` — HTTP timeout in seconds
- `--retries 1` — retry count per request
- `--compact` — compact JSON output

## Read the output

The script emits JSON with these top-level keys when available:

- `activity_status` — Komoot activity state, e.g. `Active` or `Finished`
- `live_point` — current/last coordinates, accuracy, update age, and source label
- `tour` — planned tour metadata
- `route_match` — nearest point on the planned route, confidence, distance done/remaining, remaining D+/D-, planned altitude
- `next_profile` — short profile window ahead of the matched route point
- `warnings` — non-fatal issues, e.g. no tour ID or poor route match

If the script returns `error`, report it directly. If it returns `warnings`, surface them alongside the usable data.

## Response style

Keep responses data-first and neutral. Example:

```text
Live point: 45.52513, 9.60508, updated about a minute ago.
Matched to planned route with good confidence. Distance remaining: 2.0 km, +3 m / -1 m.
```

Do not append action instructions such as when to run, what to eat, or how to manage physical risk. A separate higher-level skill should consume this tracking state if the user asks for guidance.

## Known sharp edges

- The live page is not a streaming API. Run the helper again for each fresh check.
- Planned tour coordinates are not the recorded live track. If the athlete deviates, route-progress estimates become uncertain.
- A finished or stale live link may still return the last point but fail to fetch planned tour metadata; treat that as a warning, not a total failure.

## When not to use this skill

- The user asks what to do next based on the tracking data. Use a separate higher-level skill.
- The activity is finished and the user asks for post-run analysis. Use the normal activity-analysis workflow.
- The user asks to log the activity into the training plan. Use the repository's activity logging conventions instead.
