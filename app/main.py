from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.endpoints.portfolio import router as portfolio_router
from app.core.config import get_settings
from app.db.database import init_db, DB_AVAILABLE


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if not settings.github_token:
        print("Warning: GitHub token not configured")
    else:
        print("GitHub token configured")

    init_db(settings.database_url)

    if DB_AVAILABLE:
        print("Database connected successfully")
    else:
        print("Database not available. Using in-memory storage.")

    yield


app = FastAPI(
    title="GitFolio API",
    description="Backend for GitFolio portfolio generator",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "https://gitfolio-charm.lovable.app",
        "https://gitfolio-steel.vercel.app",
        "https://gitfolio-g59co4vp2-abhishek-mj-s-projects.vercel.app",
        "https://gitfolio-six.vercel.app",
        "https://gitfolio-anj8ztc9q-abhishek-mj-s-projects.vercel.app",
        "https://gitfolio-37078ad2c-abhishek-mj-s-projects.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(portfolio_router, prefix="/api/v1", tags=["Portfolio"])
