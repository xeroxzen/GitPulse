import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from .app import app

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 