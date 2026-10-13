from datetime import datetime

from pydantic import BaseModel


class Repository(BaseModel):
    """Basic information about a GitHub repository."""

    id: int
    name: str
    full_name: str
    description: str | None
    html_url: str
    language: str | None
    stargazers_count: int
    forks_count: int
    default_branch: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime | None
