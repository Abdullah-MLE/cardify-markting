"""FastAPI Application Entry Point."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers.auth_router import router as auth_router
from backend.api.routers.company_router import router as company_router
from backend.api.routers.campaign_router import router as campaign_router
from backend.api.routers.content_router import router as content_router
from backend.api.routers.template_router import router as template_router

# Initialize FastAPI App
app = FastAPI(
    title="Cardify Marketing API",
    version="2.0.0",
    description="API for content generation and management"
)

# CORS Middleware (Allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(company_router, prefix="/api/v1")
app.include_router(campaign_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(template_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Cardify Marketing API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
