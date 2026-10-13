from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from reposentry.models.issue import GitHubUser


class PullRequest(BaseModel):
    """GitHub pull request information used by RepoSentry."""

    number: int
    title: str
    html_url: str
    state: Literal["open", "closed"]
    user: GitHubUser
    draft: bool
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None
