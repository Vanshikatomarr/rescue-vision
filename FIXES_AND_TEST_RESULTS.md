# Rescue Vision - changes and verification

## Implemented
- Retained the existing screenshot-inspired React tactical UI and existing FastAPI/YOLO pipeline, rather than replacing them with fake demo data.
- Added a Rescue Planner navigation item and a functional interactive 12x12 grid page.
- Added POST `/api/routes/plan` with Dijkstra routing, obstacle validation, shortest-step and risk-weighted modes. Risk values can be passed to the API, but the current UI does not have a risk editor.
- Route output is explicitly simulated, not GPS/real-world navigation.

## Verification performed
- Python backend syntax compilation: PASS (`python -m compileall -q backend/app`).
- Frontend build: NOT VERIFIED. Dependency installation exceeded the execution time limit; run `npm install` then `npm run build` on your computer.
- Backend runtime, YOLO image/video inference, Windows startup scripts, and integration: NOT VERIFIED in this environment because Ultralytics and full backend dependencies are not installed.

## Known limitations
- Existing features have not all been tested or repaired; some may require further debugging on Windows.
- YOLO weights are included from the uploaded archive; no new model training was performed.
- The safest route only differs from fastest when a nonzero risk matrix is supplied via API.
- A single image cannot supply accurate real-world rescue coordinates.
