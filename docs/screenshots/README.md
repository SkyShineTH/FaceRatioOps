# Screenshots

UI screenshots of the public deployment at <https://faceratioops.skyshine.online/>,
used in the project `README.md` and portfolio evidence.

| File | Page |
| --- | --- |
| `workbench.png` | Inference workbench (`/`) in its guided empty state |
| `architecture.png` | Interactive deployment topology (`/architecture`) |
| `api-docs.png` | OpenAPI / Swagger UI (`/docs`) |

The workbench screenshot is captured in its empty state, so no face image
appears in committed screenshots.

## Refreshing

Captured headless with Microsoft Edge. Re-run after a frontend change:

```powershell
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$base = "$((Resolve-Path .).Path)\docs\screenshots"
& $edge --headless=new --disable-gpu --no-sandbox --window-size=1440,1000 `
  --screenshot="$base\workbench.png" "https://faceratioops.skyshine.online/"
& $edge --headless=new --disable-gpu --no-sandbox --window-size=1440,1100 `
  --screenshot="$base\architecture.png" "https://faceratioops.skyshine.online/architecture"
& $edge --headless=new --disable-gpu --no-sandbox --window-size=1440,1100 `
  --virtual-time-budget=10000 --run-all-compositor-stages-before-draw `
  --screenshot="$base\api-docs.png" "https://faceratioops.skyshine.online/docs"
```

The Swagger page needs the render-delay flags so it is not captured on its
loading spinner.
