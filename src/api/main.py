"""FastAPI main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
import logging

logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="Production Planner API",
    description="Distributed production planning with multi-agent scheduling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    logger.info("Production Planner API starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Production Planner API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)