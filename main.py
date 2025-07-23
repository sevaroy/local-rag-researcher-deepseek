"""
FastAPI LineBot Application
"""

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.assistant.graph import researcher

from linebot import LineBotApi
from linebot_service.services import LineBotHandler, MessageRouter, ResearchService, SessionManager, FileHandler, ConfigurationService
from linebot_service.utils import ErrorResponseFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI LineBot RAG Researcher",
    description="LINE Bot integration with RAG research assistant",
    version="1.0.0"
)

# Environment variables
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

# Initialize LINE Bot API
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None

# Initialize services
session_manager = SessionManager()
file_handler = FileHandler(line_bot_api=line_bot_api) if line_bot_api else None
config_service = ConfigurationService()
research_service = ResearchService(researcher_graph=researcher)
message_router = MessageRouter(line_bot_api=line_bot_api) if line_bot_api else None

# Initialize LINE Bot handler
linebot_handler = LineBotHandler(
    channel_secret=LINE_CHANNEL_SECRET, 
    channel_access_token=LINE_CHANNEL_ACCESS_TOKEN
) if LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN else None

# Connect services if available
if linebot_handler and message_router:
    linebot_handler.set_message_router(message_router)
    message_router.set_services(
        session_manager=session_manager,
        research_service=research_service,
        file_handler=file_handler,
        config_service=config_service
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    status = "OK" if linebot_handler else "CONFIGURED (Missing LINE credentials)"
    return {
        "message": "FastAPI LineBot RAG Researcher is running", 
        "status": status
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FastAPI LineBot RAG Researcher",
        "version": "1.0.0",
        "line_configured": bool(linebot_handler)
    }


@app.post("/webhook")
async def webhook(request: Request):
    """LINE Bot webhook endpoint"""
    if not linebot_handler:
        logger.error("LINE Bot handler not configured")
        return JSONResponse(
            status_code=503,
            content={"error": "LINE Bot not configured. Please set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN."}
        )  

    try:
        return await linebot_handler.handle_webhook(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook handling error: {e}")
        error_response = ErrorResponseFactory.service_unavailable()
        return JSONResponse(
            status_code=500,
            content=error_response.to_dict()
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


# Background task to clean up expired sessions
@app.on_event("startup")
async def setup_background_tasks():
    """Set up background tasks"""
    logger.info("FastAPI LineBot RAG Researcher starting up...")  

    # Check LINE configuration
    if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE Bot not fully configured. Set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN environment variables.")
    else:
        logger.info("LINE Bot configured successfully.")  

    # Perform initial session cleanup
    try:
        cleaned_count = await session_manager.cleanup_expired_sessions()
        logger.info(f"Cleaned up {cleaned_count} expired sessions on startup")
    except Exception as e:
        logger.error(f"Error during startup session cleanup: {e}")

# 應用程式啟動指南
# 使用 uvicorn 啟動:
# $ uvicorn main:app --host 0.0.0.0 --port 8000 --reload
#
# 或者使用 gunicorn 搭配 uvicorn worker 在生產環境中啟動:
# $ gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app