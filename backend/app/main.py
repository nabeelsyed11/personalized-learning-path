from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

# Import database and models
from .database import engine, Base
from .models import *

# Import API routers
from .api.endpoints import profile, recommend, courses, chat

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Personalized Learning Path API",
    description="API for generating and managing personalized learning paths based on skills and aspirations",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(profile.router, prefix="/api", tags=["profiles"])
app.include_router(recommend.router, prefix="/api", tags=["recommendations"])
app.include_router(courses.router, prefix="/api", tags=["courses"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Personalized Learning Path API"}

# For development
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
