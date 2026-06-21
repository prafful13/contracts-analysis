# contracts-analysis

Options screener dashboard. Single Streamlit process — no separate backend server.

## Entry point

`dashboard.py` — the only file to edit for UI or screener logic changes.
Service logic: `backend/src/wtf_options/services/options_service.py`
Default tickers/filters: `config.yaml`

## Key commands

```bash
uv run inv run            # local dev → http://localhost:8501
uv run inv docker-build   # build image (cri-dockerd: no import step needed)
uv run inv k8s-apply      # deploy → http://localhost:30502
uv run inv k8s-restart    # rolling restart after docker-build
uv run inv k8s-status     # check pod health
uv run inv k8s-logs       # stream logs
```

## Dockerfile gotcha

`pyproject.toml` has `[tool.setuptools.packages.find] where = ["backend/src"]`. When running
`uv sync` before `backend/` is copied in, setuptools can't find the directory and fails.
Always use `--no-install-project`:

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache --no-install-project
COPY backend/ ./backend/
```

## CSS gotcha

Never apply styles to bare `div` or `span` selectors — Streamlit uses them for internal
icon elements (expander arrows etc.) and overriding font-family makes class names appear
as visible text. Target `data-testid` attributes and specific element types instead.

## k8s

- Namespace `contracts-analysis` is owned by k3s-dev (`uv run inv bootstrap` — one-time).
- No `namespace.yaml` in `k8s/` — k3s-dev manages it.
- `config.yaml` is mounted as a ConfigMap volume — change tickers/filters and `k8s-restart`, no rebuild needed.
- `imagePullPolicy: Never` — Rancher Desktop cri-dockerd mode makes Docker images visible to k3s directly.
