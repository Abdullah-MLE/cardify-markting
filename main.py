"""FastAPI Application Entry Point"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.company_routes import router as company_router
from app.api.routes.templates_routes import router as template_router
from app.api.routes.weekly_plan_routes import router as weekly_plan_router
from app.api.routes.content_routes import router as content_router
from app.api.routes.audio_routes import router as audio_router


# Initialize FastAPI App
app = FastAPI(
    title="AgenticAI API",
    version="1.0.0",
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
app.include_router(company_router, prefix="/api/v1")
app.include_router(template_router, prefix="/api/v1")
app.include_router(weekly_plan_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(audio_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "AgenticAI API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the API with uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
