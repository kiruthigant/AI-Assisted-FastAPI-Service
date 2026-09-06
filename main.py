import time
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

from schemas import FeedbackRequest, FeedbackAnalysis
from services.ai_service import LLMService, AIServiceException

# Load environment variables
load_dotenv()

# Basic logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Assisted Feedback Analyzer", version="1.0.0")

# Custom Rate Limiter
RATE_LIMIT = 10 # Requests
RATE_LIMIT_PERIOD = 60 # Seconds
rate_limit_records = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    # Clean up old records
    rate_limit_records[client_ip] = [
        timestamp for timestamp in rate_limit_records[client_ip] 
        if now - timestamp < RATE_LIMIT_PERIOD
    ]
    
    if len(rate_limit_records[client_ip]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."}
        )
        
    rate_limit_records[client_ip].append(now)
    response = await call_next(request)
    return response

@app.middleware("http")
async def latency_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} - Latency: {process_time:.4f}s")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."}
    )

@app.exception_handler(AIServiceException)
async def ai_service_exception_handler(request: Request, exc: AIServiceException):
    logger.error(f"AI Service Exception: {str(exc)}")
    return JSONResponse(
        status_code=502,
        content={"detail": "Error processing request with the AI provider.", "error": str(exc)}
    )

# Dependency injection for the LLM service
def get_llm_service():
    return LLMService()

@app.post("/api/v1/analyze", response_model=FeedbackAnalysis)
async def analyze_feedback(
    request: FeedbackRequest, 
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Ingest unstructured customer feedback, process it with an LLM, and return validated structured data.
    """
    result = llm_service.analyze_feedback(request.feedback_text)
    return result
