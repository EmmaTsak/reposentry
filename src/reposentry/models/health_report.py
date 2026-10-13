from pydantic import BaseModel


class HealthDeduction(BaseModel):
    """A single reason for reducing a repository health score."""

    reason: str
    points: int


class RepositoryHealthReport(BaseModel):
    """Calculated repository health summary."""

    score: int
    stale_issue_count: int
    stale_pull_request_count: int
    deductions: list[HealthDeduction]
