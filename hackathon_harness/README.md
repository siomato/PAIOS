# PAIOS Hackathon Harness V2

This version fixes the demo controls so button clicks immediately return control to the dashboard while the browser/laptop workflow runs in a background thread.

Fixes:
- Demo buttons visibly trigger commands.
- UI shows command-start errors.
- Live telemetry continues updating while Playwright runs.
- `Search Python latest release and send it to Notepad` now correctly selects the Browser -> Laptop demo.
- No changes are made to the main PAIOS backend.

Run from the PAIOS virtual environment:

    cd D:\PAIOS\hackathon_harness
    python hackathon_harness.py

Open:

    http://127.0.0.1:8765
