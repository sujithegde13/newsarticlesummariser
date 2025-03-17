import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from utils import NewsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="News Analyzer API",
    description="API for analyzing company news with sentiment analysis and Hindi TTS",
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

# Initialize the NewsAnalyzer
news_analyzer = NewsAnalyzer()

# Cache for storing analysis results
analysis_cache = {}

# Models
class CompanyRequest(BaseModel):
    company_name: str

class AnalysisResponse(BaseModel):
    status: str
    task_id: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None

class AnalysisStatusResponse(BaseModel):
    status: str
    task_id: str
    completed: bool
    data: Optional[Dict[str, Any]] = None

# Background tasks store
background_tasks = {}

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {"message": "News Analyzer API is running"}

@app.post("/analyze-company", response_model=AnalysisResponse)
async def analyze_company(request: CompanyRequest, background_tasks: BackgroundTasks):
    """
    Start a company news analysis task
    
    This endpoint initiates a background task to analyze news articles
    related to the specified company, perform sentiment analysis,
    and generate a Hindi TTS output.
    """
    company_name = request.company_name.strip()
    
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name cannot be empty")
    
    # Check if we already have cached results
    if company_name in analysis_cache:
        return {
            "status": "success",
            "task_id": company_name,
            "message": "Analysis found in cache",
            "data": analysis_cache[company_name]
        }
    
    # Generate a task ID
    task_id = f"task_{company_name.replace(' ', '_').lower()}"
    
    # Define the background task
    async def analyze_task():
        try:
            # Perform the analysis
            result = await news_analyzer.analyze_company_news(company_name)
            
            # Cache the result
            analysis_cache[company_name] = result
            
            # Update the task status
            background_tasks[task_id] = {
                "completed": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error in background task for {company_name}: {e}")
            background_tasks[task_id] = {
                "completed": True,
                "error": str(e)
            }
    
    # Initialize the background task status
    background_tasks[task_id] = {
        "completed": False
    }
    
    # Start the background task
    asyncio.create_task(analyze_task())
    
    return {
        "status": "processing",
        "task_id": task_id,
        "message": f"Analysis started for {company_name}",
        "data": None
    }

@app.get("/task-status/{task_id}", response_model=AnalysisStatusResponse)
async def get_task_status(task_id: str):
    """
    Check the status of an analysis task
    
    This endpoint allows clients to poll for the completion
    of a previously initiated analysis task.
    """
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task_info = background_tasks[task_id]
    
    if task_info["completed"]:
        if "error" in task_info:
            return {
                "status": "failed",
                "task_id": task_id,
                "completed": True,
                "data": {"error": task_info["error"]}
            }
        else:
            return {
                "status": "completed",
                "task_id": task_id,
                "completed": True,
                "data": task_info["result"]
            }
    else:
        return {
            "status": "processing",
            "task_id": task_id,
            "completed": False,
            "data": None
        }

@app.get("/available-companies")
async def get_available_companies():
    """
    Get a list of companies that have been analyzed and cached
    
    This endpoint returns a list of company names that have
    already been analyzed and are available in the cache.
    """
    return {
        "companies": list(analysis_cache.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": True}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
