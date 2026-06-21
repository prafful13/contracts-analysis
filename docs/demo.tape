Output docs/demo.gif
Set Theme { Background "#0D1117" Foreground "#E6EDF3" }
Set FontSize 14
Set Width 900
Set Height 500
Set Framerate 24
Set PlaybackSpeed 0.8

Type "# contracts-analysis — options screener"
Sleep 600ms
Enter

Sleep 400ms
Type "uv run inv run"
Sleep 500ms
Enter

Sleep 3000ms

Type "# Dashboard running at http://localhost:8501"
Sleep 600ms
Enter
Sleep 400ms

Type "# Configure tickers in config.yaml, then click ▶ Run Scan"
Sleep 600ms
Enter
Sleep 400ms

Type "# Income Screener: sells ranked by Annual% (progress bar = return magnitude)"
Sleep 600ms
Enter
Sleep 400ms

Type "# Buy Screener: calls/puts ranked by composite score (delta × 100 + liquidity)"
Sleep 600ms
Enter
Sleep 400ms

Type "# Export CSV per table — button appears below results"
Sleep 600ms
Enter
Sleep 400ms

Type "# To deploy on local k3s:"
Sleep 400ms
Enter
Type "uv run inv bootstrap && uv run inv docker-build && uv run inv k8s-apply"
Sleep 600ms
Enter

Sleep 2000ms
Type "# → http://localhost:30502"
Sleep 1200ms
Enter
Sleep 800ms
