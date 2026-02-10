"""
FastAPI web app — exposes the bot's intelligence via HTTP for the React frontend.
"""

import secrets
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config.settings import settings
from src.services.query_analyzer import query_analyzer
from src.services.data_processor import data_processor
from src.services.sheets_service import sheets_service
from src.services.response_generator import response_generator
from src.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory set of valid session tokens (reset on restart, fine for simple auth)
_valid_tokens: set = set()

security = HTTPBearer()


# ── Request / Response models ──────────────────────────────────────────────────

class AuthRequest(BaseModel):
    password: str

class AuthResponse(BaseModel):
    token: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    query_type: str


# ── Auth helper ────────────────────────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in _valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return credentials.credentials


# ── App factory ────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(title="RV Fund Bot API", docs_url=None, redoc_url=None)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tightened per-domain after first deploy if needed
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/auth", response_model=AuthResponse)
    async def login(body: AuthRequest):
        if body.password != settings.web_password:
            raise HTTPException(status_code=401, detail="Wrong password")
        token = secrets.token_hex(32)
        _valid_tokens.add(token)
        logger.info("Web login successful")
        return AuthResponse(token=token)

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(body: ChatRequest, _token: str = Depends(verify_token)):
        try:
            # Analyze intent
            intent = await query_analyzer.analyze(
                body.message, body.conversation_history or []
            )

            # Fetch data and process
            if intent.query_type == "general_chat":
                processed_data = None
            else:
                fund_df = await sheets_service.get_fund_metrics()
                portfolio_df = await sheets_service.get_portfolio_data()
                processed_data = data_processor.process_query(intent, fund_df, portfolio_df)

            # Generate response
            response_text = await response_generator.generate(
                processed_data, body.message, body.conversation_history or []
            )

            return ChatResponse(
                response=response_text,
                query_type=str(intent.query_type),
            )

        except Exception as e:
            logger.error("Error in /api/chat", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Internal error processing your query")

    return app
