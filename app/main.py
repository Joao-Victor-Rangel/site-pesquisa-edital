from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from app.database import engine, get_db
from app.models import Base
from app.routers import auth, opportunities, users, agents, search
from app.core.crew_manager import CrewManager
from app.core.scheduler import start_scheduler

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FundingAI API",
    description="API para busca inteligente de oportunidades de financiamento",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["opportunities"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

# Initialize CrewAI and scheduler
crew_manager = CrewManager()
start_scheduler()

@app.get("/")
async def root():
    return {"message": "FundingAI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )