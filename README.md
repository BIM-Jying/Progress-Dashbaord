# XER / MPP progress dashboard generator

Drop a Primavera `.xer`, MS Project `.mpp` (or Project `.xml`) into `input/`, push, and GitHub builds a colorful dashboard
(EVMS, S-curves by labor / non-labor / phase / WBS L1-3 / activity code, resource histograms, look-ahead, early delays, slicers) for each file.

## Use it
1. Create a GitHub repo (private recommended) and push this folder.
2. Put your files in `input/` and commit.
3. Open **Actions → Build dashboards → latest run → Artifacts → dashboards**, unzip and open `index.html`
   (each dashboard is a single self-contained HTML file, data embedded).
4. Optional hosting: Settings → Pages → Source = GitHub Actions, then add repo variable `DEPLOY_PAGES = true`.
   Warning: Pages sites can be public and your schedule data is embedded in the page. Use only if you accept that.

## Local / Codespaces / Docker
`pip install -r requirements.txt` (needs Java 11+ for .mpp), then `python build.py input docs`.
Docker: `docker build -t dash . && docker run --rm -v "$PWD/input:/app/input" -v "$PWD/docs:/app/docs" dash`

## Notes
- .xer and .xml need no Java; .mpp is converted with MPXJ. Set the Status Date in MS Project first (used as data date).
- The page itself (template/dashboard.html) also has an Upload button for .xer / .xml.
- Planned = target/baseline dates, actual = actual dates to data date, earned = target x % complete; phases are keyword-based.
