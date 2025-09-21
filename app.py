from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import os
from dotenv import load_dotenv

from crew import SginGPTCrew

# Load environment variables
load_dotenv()

app = FastAPI(
    title="SignGPT Crew Server",
    description="API server for processing ASL tokens using AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ASL dataset at startup
try:
    with open("./data/english_words.json", "r", encoding="utf-8") as f:
        asl_dataset_raw = json.load(f)
    asl_dataset = [asl_dataset_raw[word].upper() for word in asl_dataset_raw]
except FileNotFoundError as exc:
    raise RuntimeError(
        "ASL dataset file not found at ./data/english_words.json") from exc

# Pydantic models for request/response


class ProcessTokensRequest(BaseModel):
    words: List[str] = Field(
        ...,
        description="List of ASL tokens to process",
        example=["YOU", "NAME", "WHAT"]
    )


class ProcessTokensResponse(BaseModel):
    result: str = Field(description="Final processed result")


class HealthResponse(BaseModel):
    status: str
    message: str
    asl_dataset_size: int


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

# Initialize crew instance


def get_crew_instance():
    """Get a new crew instance"""
    return SginGPTCrew()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "SignGPT Crew Server is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check if OpenAI API key is configured
    openai_key_configured = bool(os.getenv("OPENAI_API_KEY"))

    return HealthResponse(
        status="healthy" if openai_key_configured else "warning",
        message="Service is running" if openai_key_configured else "Service running but OPENAI_API_KEY not configured",
        asl_dataset_size=len(asl_dataset)
    )


@app.post("/process-tokens", response_model=ProcessTokensResponse)
async def process_tokens(request: ProcessTokensRequest):
    """
    Process ASL tokens through the SignGPT crew workflow

    This endpoint takes a list of ASL tokens and processes them through
    multiple AI agents to generate natural language output.
    Returns only the final result string.
    """
    try:
        # Validate OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY not configured. Please set it in your environment or .env file."
            )

        # Validate input
        if not request.words:
            raise HTTPException(
                status_code=400,
                detail="Words list cannot be empty"
            )

        # Process tokens through the crew
        crew_instance = get_crew_instance()
        result = crew_instance.sgin_gpt_crew().kickoff(
            inputs={'words': request.words, 'ASL_dataset': asl_dataset}
        )

        # Return only the result
        return ProcessTokensResponse(result=str(result))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing tokens: {str(e)}"
        ) from e


@app.get("/asl-dataset", response_model=Dict[str, Any])
async def get_asl_dataset():
    """Get information about the available ASL dataset"""
    return {
        "total_words": len(asl_dataset),
        "sample_words": asl_dataset[:20],  # First 20 words as sample
        "description": "Available ASL vocabulary tokens"
    }


@app.post("/validate-tokens", response_model=Dict[str, Any])
async def validate_tokens(tokens: List[str]):
    """
    Validate if given tokens exist in the ASL dataset
    """
    validation_results = {}
    valid_tokens = []
    invalid_tokens = []

    for token in tokens:
        token_upper = token.upper()
        if token_upper in asl_dataset:
            valid_tokens.append(token_upper)
            validation_results[token] = {
                "valid": True, "normalized": token_upper}
        else:
            invalid_tokens.append(token)
            validation_results[token] = {"valid": False, "normalized": None}

    return {
        "validation_results": validation_results,
        "summary": {
            "total_tokens": len(tokens),
            "valid_count": len(valid_tokens),
            "invalid_count": len(invalid_tokens),
            "valid_tokens": valid_tokens,
            "invalid_tokens": invalid_tokens
        }
    }

# Error handlers


@app.exception_handler(404)
async def not_found_handler(request, exc):  # noqa: ARG001
    return {"error": "Not found", "detail": "The requested resource was not found"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):  # noqa: ARG001
    return {"error": "Internal server error", "detail": "An unexpected error occurred"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
