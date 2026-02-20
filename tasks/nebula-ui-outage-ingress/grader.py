#!/usr/bin/env python3
import time
import requests
from apex_arena._types import GradingResult

HEADERS = {
    "User-Agent": "apex-grader"
}

def safe_check(url, retries=5, delay=2):
    """
    Perform an HTTP GET with retries to handle Kubernetes
    eventual consistency and ingress propagation delays.
    SSL verification is disabled to support self-signed
    certificates in test environments.
    """
    for _ in range(retries):
        try:
            r = requests.get(
                url,
                timeout=5,
                headers=HEADERS,
                allow_redirects=True,
                verify=False
            )
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False

def grade(transcript: str) -> GradingResult:
    subscores = {}
    feedback = []

    # UI availability check
    ui_ok = safe_check("https://ui.devops.local/")
    subscores["ui_access"] = 1.0 if ui_ok else 0.0
    feedback.append("✓ UI reachable" if ui_ok else "✗ UI not reachable")

    # Static asset check
    static_ok = safe_check("https://ui.devops.local/static/app.js")
    subscores["static_assets"] = 1.0 if static_ok else 0.0
    feedback.append("✓ Static assets load" if static_ok else "✗ Static assets missing")

    # API health check (must remain healthy)
    api_ok = safe_check("https://api.devops.local/health")
    subscores["api_health"] = 1.0 if api_ok else 0.0
    feedback.append("✓ API healthy" if api_ok else "✗ API unhealthy")

    weights = {
        "ui_access": 0.4,
        "static_assets": 0.4,
        "api_health": 0.2
    }

    # Hard failure if API is unhealthy
    if not api_ok:
        return GradingResult(
            score=0.0,
            subscores=subscores,
            weights=weights,
            feedback=" | ".join(feedback)
        )

    final_score = sum(subscores[k] * weights[k] for k in weights)

    return GradingResult(
        score=final_score,
        subscores=subscores,
        weights=weights,
        feedback=" | ".join(feedback)
    )