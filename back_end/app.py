"""
FastAPI application for Lughati AI backend.
Provides the /api/generate endpoint for text processing and serves the frontend.
"""
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Tuple
import os
import time
import logging
from collections import defaultdict
from back_end.model import generate_text, MODE_PROMPTS


app = FastAPI(
    title="Lughati AI API",
    description="Arabic Grammar & Rewriting Assistant API",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting: in-memory storage
# Structure: {ip: [timestamp1, timestamp2, ...]}
rate_limit_store = defaultdict(list)
# Structure: {ip: last_request_timestamp} for minimum interval check
last_request_time = {}
RATE_LIMIT_MAX_REQUESTS = 30  # Increased to 30 per window
RATE_LIMIT_WINDOW_SECONDS = 600  # 10 minutes
MIN_REQUEST_INTERVAL_SECONDS = 1  # Minimum 1 second between requests
MAX_TEXT_LENGTH = 2500

# Daily cap for free users (no BYO key)
# Structure: {ip: {"date": "YYYY-MM-DD", "count": N}}
daily_cap_store = defaultdict(dict)
FREE_TIER_DAILY_LIMIT = 5


class GenerateRequest(BaseModel):
    """Request model for /api/generate endpoint."""
    text: str = Field(..., description="The input text to process")
    mode: str = Field(..., description="The processing mode")


class GenerateResponse(BaseModel):
    """Response model for /api/generate endpoint."""
    result: str = Field(..., description="The generated/processed text")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root():
    """Serve the frontend index.html."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "front_end", "index.html")
    return FileResponse(frontend_path)


@app.get("/api/modes")
async def get_modes():
    """Get list of available modes."""
    return {
        "modes": [
            {
                "id": mode_id,
                "name": mode_id.replace("_", " ").title()
            }
            for mode_id in MODE_PROMPTS.keys()
        ]
    }


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded IP (if behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(ip: str) -> Tuple[bool, str]:
    """
    Check if IP has exceeded rate limit.
    
    Returns:
        (allowed: bool, reason: str)
        - allowed: True if request is allowed, False if blocked
        - reason: "ok", "too_fast", or "rate_window" for logging
    """
    now = time.time()
    
    # 1. Check minimum interval (prevents double-clicks and rapid-fire requests)
    if ip in last_request_time:
        time_since_last = now - last_request_time[ip]
        if time_since_last < MIN_REQUEST_INTERVAL_SECONDS:
            return False, "too_fast"
    
    # 2. Clean old entries (prune timestamps outside the window)
    # Only keep timestamps within the last RATE_LIMIT_WINDOW_SECONDS
    cutoff_time = now - RATE_LIMIT_WINDOW_SECONDS
    rate_limit_store[ip] = [
        ts for ts in rate_limit_store[ip]
        if ts > cutoff_time
    ]
    
    # 3. Check if limit exceeded
    current_count = len(rate_limit_store[ip])
    if current_count >= RATE_LIMIT_MAX_REQUESTS:
        return False, "rate_window"
    
    # 4. Record this request
    rate_limit_store[ip].append(now)
    last_request_time[ip] = now
    
    return True, "ok"


def check_daily_cap(ip: str) -> bool:
    """
    Check if IP has exceeded daily free tier limit.
    Returns True if allowed, False if daily cap exceeded.
    Only applies to free users (no BYO key).
    """
    from datetime import date
    today = date.today().isoformat()  # YYYY-MM-DD
    
    # Get or initialize daily count for this IP
    ip_data = daily_cap_store[ip]
    
    # Reset if it's a new day
    if ip_data.get("date") != today:
        ip_data["date"] = today
        ip_data["count"] = 0
    
    # Check if limit exceeded
    if ip_data["count"] >= FREE_TIER_DAILY_LIMIT:
        return False
    
    # Increment count
    ip_data["count"] = ip_data.get("count", 0) + 1
    return True


def has_server_api_key() -> bool:
    """
    Check if server has OPENAI_API_KEY configured.
    Returns True if key exists, False otherwise.
    Never returns the actual key value.
    """
    try:
        from back_end.config import get_openai_api_key
        get_openai_api_key()
        return True
    except ValueError:
        return False


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    request_obj: Request,
    x_openai_key: Optional[str] = Header(None, alias="X-OPENAI-KEY")
):
    """
    Generate corrected/rewritten/translated text based on mode.
    
    Args:
        request: GenerateRequest containing text and mode
        request_obj: FastAPI Request object for IP extraction
        x_openai_key: Optional OpenAI API key from header
    
    Returns:
        GenerateResponse with the result
    
    Raises:
        HTTPException: If input is invalid or processing fails
    """
    client_ip = get_client_ip(request_obj)
    has_byo_key = bool(x_openai_key and x_openai_key.strip())
    
    try:
        # 1. Check text length (applies to everyone)
        if len(request.text) > MAX_TEXT_LENGTH:
            error_msg = f"Text length exceeds maximum of {MAX_TEXT_LENGTH} characters"
            logger.warning(f"Blocked request from {client_ip}: text too long ({len(request.text)} chars)")
            raise HTTPException(
                status_code=400,
                detail={"error": error_msg}
            )
        
        # 2. Check rate limit (applies to everyone, only for POST /api/generate)
        allowed, reason = check_rate_limit(client_ip)
        if not allowed:
            if reason == "too_fast":
                error_msg = "Too many requests. Please wait a second and try again."
                logger.info(
                    f"Rate limit blocked: ip={client_ip}, reason={reason}, "
                    f"min_interval={MIN_REQUEST_INTERVAL_SECONDS}s"
                )
            else:  # rate_window
                current_count = len(rate_limit_store[client_ip])
                error_msg = "Rate limit exceeded. Try again later."
                logger.info(
                    f"Rate limit blocked: ip={client_ip}, reason={reason}, "
                    f"count={current_count}, limit={RATE_LIMIT_MAX_REQUESTS}, "
                    f"window={RATE_LIMIT_WINDOW_SECONDS}s"
                )
            raise HTTPException(
                status_code=429,
                detail={"error": error_msg}
            )
        
        # 3. Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail={"error": "Text cannot be empty"}
            )
        
        if not request.mode:
            raise HTTPException(
                status_code=400,
                detail={"error": "Mode is required"}
            )
        
        # 4. Check API key availability
        # If no BYO key provided, check if server has a key
        if not has_byo_key:
            if not has_server_api_key():
                # No server key and no BYO key - reject
                error_msg = "Server is not configured. Please add your own OpenAI key to continue."
                logger.warning(f"Blocked request from {client_ip}: no API key available")
                raise HTTPException(
                    status_code=400,
                    detail={"error": error_msg}
                )
            # Free tier: check daily cap (only when no BYO key)
            if not check_daily_cap(client_ip):
                error_msg = "Daily free limit reached. Add your own OpenAI key for unlimited usage (your billing) or subscribe to unlock more."
                logger.warning(f"Blocked request from {client_ip}: daily free limit exceeded")
                raise HTTPException(
                    status_code=429,
                    detail={"error": error_msg}
                )
        
        # 5. Generate text (pass API key if provided)
        # Note: x_openai_key is never logged - only passed to generate_text
        api_key = x_openai_key if has_byo_key else None
        result = generate_text(request.text, request.mode, api_key=api_key)
        
        return GenerateResponse(result=result)
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        # Log error but never log API keys or user text
        error_msg = str(e)
        logger.error(f"Error processing request from {client_ip}: {error_msg}")
        raise HTTPException(status_code=500, detail={"error": "An error occurred while processing your request. Please try again."})


# Mount static files (CSS, JS) from front_end directory
# This must be added after all route definitions to avoid conflicts
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "front_end")

# Serve static files (CSS, JS) from front_end directory
# This allows index.html to reference styles.css and script.js directly
@app.get("/styles.css")
async def serve_css():
    """Serve styles.css."""
    css_path = os.path.join(frontend_dir, "styles.css")
    return FileResponse(css_path, media_type="text/css")

@app.get("/script.js")
async def serve_js():
    """Serve script.js."""
    js_path = os.path.join(frontend_dir, "script.js")
    return FileResponse(js_path, media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)


