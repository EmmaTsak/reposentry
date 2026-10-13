from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class WorkflowRun(BaseModel):
    """GitHub Actions workflow run information used by RepoSentry."""

    id: int
    name: str
    html_url: str
    status: Literal[
        "queued",
        "in_progress",
        "completed",
        "waiting",
        "requested",
        "pending",
    ]
    conclusion: (
        Literal[
            "success",
            "failure",
            "neutral",
            "cancelled",
            "skipped",
            "timed_out",
            "action_required",
            "startup_failure",
            "stale",
        ]
        | None
    )
    created_at: datetime
    updated_at: datetime
    run_started_at: datetime | None = None
