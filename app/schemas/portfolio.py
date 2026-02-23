from pydantic import BaseModel
from typing import Optional, Any


class ProfileSchema(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: str
    followers: int
    following: int


class RepoSchema(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    html_url: str


class GitHubResponse(BaseModel):
    profile: ProfileSchema
    repos: list[RepoSchema]


class PortfolioCreate(BaseModel):
    github_username: str
    data: dict[str, Any]


class PortfolioResponse(BaseModel):
    github_username: str
    data: dict[str, Any]
    created_at: str
    updated_at: str
