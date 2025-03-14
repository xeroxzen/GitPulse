import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .app import app

# Mount static files is now handled in app.py

if __name__ == "__main__":
    uvicorn.run("gitpulse.web.app:app", host="0.0.0.0", port=8000, reload=True) 