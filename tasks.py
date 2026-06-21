from __future__ import annotations

from invoke import task

NS = "contracts-analysis"
IMAGE = "contracts-analysis:latest"


@task
def run(c):
    """Start the Streamlit dashboard locally."""
    c.run("uv run streamlit run dashboard.py")


bot = run


@task
def bootstrap(c):
    """Provision the k3s namespace via k3s-dev (one-time setup)."""
    c.run(f"k3s-dev namespace add {NS}")


@task(name="docker-build")
def docker_build(c):
    """Build the dashboard image (cri-dockerd mode: Docker images are visible to k3s directly)."""
    c.run(f"docker build -t {IMAGE} -f Dockerfile.dashboard .")


@task(name="k8s-apply")
def k8s_apply(c):
    """Apply all k8s manifests."""
    c.run("kubectl apply -f k8s/")


@task(name="k8s-status")
def k8s_status(c):
    """Show pods, services, and deployment status."""
    c.run(f"kubectl get pods,svc,deploy -n {NS}")


@task(name="k8s-logs")
def k8s_logs(c):
    """Stream dashboard pod logs."""
    c.run(f"kubectl logs -n {NS} -l app={NS} -f")


@task(name="k8s-restart")
def k8s_restart(c):
    """Rolling restart of the dashboard deployment."""
    c.run(f"kubectl rollout restart deployment/{NS} -n {NS}")


@task(name="lock-update")
def lock_update(c):
    """Regenerate requirements.lock for Bazel pip.parse()."""
    c.run("uv export --no-dev --format requirements-txt --no-hashes > requirements.lock")
