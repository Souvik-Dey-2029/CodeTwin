import os
import sys

# Ensure the repo root is on sys.path so sibling packages (e.g. analysis_engine) can be imported.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.database import engine, Base
import app.models # Ensure models are loaded for create_all

app = FastAPI(
    title="CodeTwin API",
    description="Backend API for CodeTwin - AI Digital Twin for Codebases",
    version="0.2.0",  # Updated to include reanalyze endpoint
)

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount frontend
frontend_out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "out"))

if os.path.exists(frontend_out):
    # Mount Next.js chunks and assets
    app.mount("/_next", StaticFiles(directory=os.path.join(frontend_out, "_next")), name="next_assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if not full_path or full_path == "/":
            full_path = "index.html"
            
        exact_path = os.path.join(frontend_out, full_path)
        if os.path.isfile(exact_path):
            return FileResponse(exact_path)
            
        html_path = os.path.join(frontend_out, f"{full_path}.html")
        if os.path.isfile(html_path):
            return FileResponse(html_path)
            
        index_path = os.path.join(frontend_out, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
            
        return {"error": "Frontend route not found"}
else:
    @app.get("/")
    async def root():
        return {"message": "CodeTwin API Online. Frontend not built. Run 'npm run build'."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
