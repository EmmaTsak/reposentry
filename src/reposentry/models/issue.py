from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class GitHubUser(BaseModel):
    """Basic GitHub user information."""

    login: str
    html_url: str


class Issue(BaseModel):
    """GitHub issue information used by RepoSentry."""

    number: int
    title: str
    html_url: str
    state: Literal["open", "closed"]
    user: GitHubUser
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
