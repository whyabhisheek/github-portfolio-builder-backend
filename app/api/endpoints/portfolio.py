import json
import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.db.database import get_db, DB_AVAILABLE
from app.models.portfolio import Portfolio
from app.schemas.portfolio import (
    PortfolioCreate, 
    PortfolioResponse, 
    GitHubResponse, 
    ProfileSchema, 
    RepoSchema
)
from app.core.config import get_settings

router = APIRouter()

in_memory_store = {}


@router.get("/github/{username}", response_model=GitHubResponse)
async def get_github_profile(username: str):
    settings = get_settings()
    
    if not settings.github_token:
        raise HTTPException(status_code=500, detail="GitHub token not configured")
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {settings.github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    async with httpx.AsyncClient(timeout=settings.github_api_timeout) as client:
        try:
            user_response = await client.get(
                f"https://api.github.com/users/{username}",
                headers=headers
            )
            
            if user_response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user_response.status_code == 403:
                raise HTTPException(status_code=403, detail="API rate limit exceeded")
            
            user_response.raise_for_status()
            user_data = user_response.json()
            
            repos_response = await client.get(
                f"https://api.github.com/users/{username}/repos",
                headers=headers,
                params={"sort": "stars", "per_page": 30}
            )
            repos_response.raise_for_status()
            repos_data = repos_response.json()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to connect to GitHub API")
    
    profile = ProfileSchema(
        name=user_data.get("name"),
        bio=user_data.get("bio"),
        avatar_url=user_data.get("avatar_url", ""),
        followers=user_data.get("followers", 0),
        following=user_data.get("following", 0)
    )
    
    repos = [
        RepoSchema(
            name=repo.get("name", ""),
            description=repo.get("description"),
            language=repo.get("language"),
            stars=repo.get("stargazers_count", 0),
            html_url=repo.get("html_url", "")
        )
        for repo in repos_data
    ]
    
    return GitHubResponse(profile=profile, repos=repos)


@router.post("/portfolio", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db)
):
    if not DB_AVAILABLE:
        now = datetime.utcnow().isoformat()
        in_memory_store[portfolio.github_username] = {
            "github_username": portfolio.github_username,
            "data": portfolio.data,
            "created_at": now,
            "updated_at": now
        }
        return PortfolioResponse(
            github_username=portfolio.github_username,
            data=portfolio.data,
            created_at=now,
            updated_at=now
        )
    
    try:
        existing = db.query(Portfolio).filter(
            Portfolio.github_username == portfolio.github_username
        ).first()
        
        if existing:
            existing.portfolio_data = json.dumps(portfolio.data)
            existing.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return PortfolioResponse(
                github_username=existing.github_username,
                data=json.loads(existing.portfolio_data),
                created_at=existing.created_at.isoformat(),
                updated_at=existing.updated_at.isoformat()
            )
        
        new_portfolio = Portfolio(
            github_username=portfolio.github_username,
            portfolio_data=json.dumps(portfolio.data)
        )
        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)
        
        return PortfolioResponse(
            github_username=new_portfolio.github_username,
            data=json.loads(new_portfolio.portfolio_data),
            created_at=new_portfolio.created_at.isoformat(),
            updated_at=new_portfolio.updated_at.isoformat()
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


@router.get("/portfolio/{username}", response_model=PortfolioResponse)
async def get_portfolio(username: str, db: Session = Depends(get_db)):
    if not DB_AVAILABLE:
        if username not in in_memory_store:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        data = in_memory_store[username]
        return PortfolioResponse(
            github_username=data["github_username"],
            data=data["data"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.github_username == username
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return PortfolioResponse(
            github_username=portfolio.github_username,
            data=json.loads(portfolio.portfolio_data),
            created_at=portfolio.created_at.isoformat(),
            updated_at=portfolio.updated_at.isoformat()
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
