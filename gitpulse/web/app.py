from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from ..core.repository import Repository, ContributorStats
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(
    title="GitPulse API",
    description="API for analyzing Git repositories",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

class RepositoryRequest(BaseModel):
    path: str
    is_remote: bool = False

class ContributorResponse(BaseModel):
    name: str
    email: str
    commit_count: int
    lines_added: int
    lines_deleted: int
    files_changed: int
    languages: Dict[str, int]
    total_changes: int
    percentage: float
    total_lines: int
    percentage_lines: float
    total_files: int
    percentage_files: float
    

@app.post("/analyze", response_model=List[ContributorResponse])
async def analyze_repository(request: RepositoryRequest):
    """Analyze a Git repository and return contributor statistics."""
    try:
        repo = Repository(request.path, request.is_remote)
        stats = repo.get_contributor_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/languages")
async def get_languages(request: RepositoryRequest):
    """Get language distribution in the repository."""
    try:
        repo = Repository(request.path, request.is_remote)
        languages = repo.get_top_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/")
async def root():
    """Redirect to the static index.html file."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html") 