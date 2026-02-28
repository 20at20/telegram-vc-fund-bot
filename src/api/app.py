"""
FastAPI web app — exposes the bot's intelligence via HTTP for the React frontend.
"""

import secrets
import smtplib
from contextlib import asynccontextmanager
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional

import pandas as pd
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Depends, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config.settings import settings
from src.services.query_analyzer import query_analyzer
from src.services.data_processor import data_processor
from src.services.sheets_service import sheets_service
from src.services.companies_service import companies_service
from src.services.response_generator import response_generator
from src.services.news_service import refresh_all_news, get_cached_news
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
    previous_result: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    query_type: str
    structured_data: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, str]]] = None


# ── Data serialization ────────────────────────────────────────────────────────

def _serialize_processed_data(data) -> Optional[Dict[str, Any]]:
    """Convert processed data to JSON-safe dict for the web frontend."""
    if data is None:
        return None
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return {"type": "table", "columns": [], "rows": []}
        return {
            "type": "table",
            "columns": list(data.columns),
            "rows": data.fillna("").astype(object).to_dict(orient="records"),
        }
    if isinstance(data, dict):
        if "error" in data:
            return None
        # Convert any DataFrame values nested inside the dict
        result: Dict[str, Any] = {"type": "dict"}
        for k, v in data.items():
            if isinstance(v, pd.DataFrame):
                result[k] = v.fillna("").astype(object).to_dict(orient="records")
            else:
                result[k] = v
        return result
    return None


def _generate_clarification(user_message: str) -> Dict[str, Any]:
    """Generate clarification response with options for ambiguous queries."""
    message_lower = user_message.lower().strip()

    metric_patterns = {
        "tvpi": {
            "response": "What would you like to know about TVPI?",
            "options": [
                {"label": "Current TVPI value", "query": "What is our current TVPI?"},
                {"label": "TVPI trend over time", "query": "Show TVPI trend over time"},
                {"label": "What is TVPI?", "query": "What does TVPI mean?"},
            ],
        },
        "dpi": {
            "response": "What would you like to know about DPI?",
            "options": [
                {"label": "Current DPI value", "query": "What is our current DPI?"},
                {"label": "DPI trend over time", "query": "Show DPI trend over time"},
                {"label": "What is DPI?", "query": "What does DPI mean?"},
            ],
        },
        "irr": {
            "response": "What would you like to know about IRR?",
            "options": [
                {"label": "Current IRR", "query": "What is our fund IRR?"},
                {"label": "IRR over time", "query": "Show IRR trend over time"},
                {"label": "What is IRR?", "query": "What does IRR mean?"},
            ],
        },
        "portfolio": {
            "response": "What would you like to know about the portfolio?",
            "options": [
                {"label": "All portfolio companies", "query": "Show all portfolio companies"},
                {"label": "Top 5 by return", "query": "Top 5 companies by return"},
                {"label": "Portfolio by sector", "query": "Show portfolio breakdown by sector"},
            ],
        },
    }

    for keyword, data in metric_patterns.items():
        if keyword in message_lower:
            return data

    return {
        "response": "I'm not sure what you're looking for. Try one of these:",
        "options": [
            {"label": "Fund performance", "query": "What is our current TVPI?"},
            {"label": "Top companies", "query": "Top 5 companies by return"},
            {"label": "Portfolio by sector", "query": "Show fintech companies"},
            {"label": "Recent investments", "query": "Show our 5 most recent investments"},
        ],
    }


# ── Previous result context ───────────────────────────────────────────────────

def _extract_previous_result_context(previous_result: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extract company names from previous structured result for follow-up context."""
    if not previous_result:
        return None

    rows = previous_result.get("rows")
    if not rows or not isinstance(rows, list):
        return None

    # Extract company names from the rows
    company_names = []
    for row in rows:
        for key in ["Company Name", "company name", "Company", "Name", "company", "name"]:
            if key in row and row[key]:
                company_names.append(str(row[key]))
                break

    if not company_names:
        return None

    return "Companies: " + ", ".join(company_names)


# ── Auth helper ────────────────────────────────────────────────────────────────

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials not in _valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return credentials.credentials


# ── Startup / shutdown ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start news scheduler on startup; stop it cleanly on shutdown."""
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        refresh_all_news,
        trigger="cron",
        hour=7,
        minute=0,
        id="daily_news_refresh",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("News scheduler started — running initial fetch")
    await refresh_all_news()
    yield
    scheduler.shutdown(wait=False)
    logger.info("News scheduler stopped")


# ── App factory ────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(title="RV Fund Bot API", docs_url=None, redoc_url=None, lifespan=lifespan)

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
            # Build previous result context for follow-up queries
            previous_result_context = _extract_previous_result_context(body.previous_result)

            # Analyze intent
            intent = await query_analyzer.analyze(
                body.message, body.conversation_history or [], previous_result_context
            )

            # Handle ambiguous queries with clarification
            if intent.query_type == "unknown":
                clarification = _generate_clarification(body.message)
                return ChatResponse(
                    response=clarification["response"],
                    query_type="clarification",
                    options=clarification["options"],
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
                structured_data=_serialize_processed_data(processed_data),
            )

        except Exception as e:
            logger.error("Error in /api/chat", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Internal error processing your query")

    @app.get("/api/deals")
    async def deals(_token: str = Depends(verify_token)):
        try:
            df, links = await sheets_service.get_deals_data()
            if df.empty:
                return {"columns": [], "rows": [], "links": {}}
            return {
                "columns": list(df.columns),
                "rows": df.fillna("").astype(object).to_dict(orient="records"),
                "links": links,
            }
        except Exception as e:
            logger.error("Error in /api/deals", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error fetching deals data")

    @app.get("/api/experts")
    async def experts(_token: str = Depends(verify_token)):
        try:
            df, links = await sheets_service.get_experts_data()
            if df.empty:
                return {"columns": [], "rows": [], "links": {}}
            return {
                "columns": list(df.columns),
                "rows": df.fillna("").astype(object).to_dict(orient="records"),
                "links": links,
            }
        except Exception as e:
            logger.error("Error in /api/experts", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error fetching experts data")

    @app.get("/api/asks")
    async def asks(_token: str = Depends(verify_token)):
        try:
            df, links = await sheets_service.get_asks_data()
            if df.empty:
                return {"columns": [], "rows": [], "links": {}}
            return {
                "columns": list(df.columns),
                "rows": df.fillna("").astype(object).to_dict(orient="records"),
                "links": links,
            }
        except Exception as e:
            logger.error("Error in /api/asks", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error fetching asks data")

    @app.get("/api/fund_metrics")
    async def fund_metrics(_token: str = Depends(verify_token)):
        try:
            fund_df = await sheets_service.get_fund_metrics()
            metric_names = ["TVPI", "IRR", "DPI", "RV investments, $K", "Portfolio Value", "Realised Value"]
            metrics = []
            for name in metric_names:
                result = data_processor.process_fund_metric(fund_df, name, "latest")
                if "error" not in result:
                    metrics.append(result)
            return {"metrics": metrics}
        except Exception as e:
            logger.error("Error in /api/fund_metrics", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error fetching fund metrics")

    @app.get("/api/companies")
    async def companies(
        _token: str = Depends(verify_token),
        q: str = "",
        industry: str = "",
        country: str = "",
        stage: str = "",
        limit: int = 50,
        offset: int = 0,
    ):
        try:
            return companies_service.search(q, industry, country, stage, limit, offset)
        except Exception as e:
            logger.error("Error in /api/companies", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error searching companies")

    @app.get("/api/news")
    async def news(_token: str = Depends(verify_token)):
        try:
            return get_cached_news()
        except Exception as e:
            logger.error("Error in /api/news", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Error fetching news")

    @app.post("/api/submit_deal")
    async def submit_deal(
        company_name: str = Form(...),
        available_info: str = Form(""),
        thoughts: str = Form(""),
        deck: UploadFile | None = File(None),
        _token: str = Depends(verify_token),
    ):
        if not settings.gmail_user or not settings.gmail_app_password:
            raise HTTPException(status_code=503, detail="Email delivery is not configured")
        try:
            msg = MIMEMultipart()
            msg["From"] = settings.gmail_user
            msg["To"] = settings.gmail_user
            msg["Subject"] = f"Deal submitted: {company_name}"

            body_parts = [f"Company: {company_name}"]
            if available_info:
                body_parts.append(f"\nAvailable information:\n{available_info}")
            if thoughts:
                body_parts.append(f"\nThoughts:\n{thoughts}")
            msg.attach(MIMEText("\n".join(body_parts), "plain"))

            if deck and deck.filename:
                file_bytes = await deck.read()
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_bytes)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{deck.filename}"')
                msg.attach(part)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(settings.gmail_user, settings.gmail_app_password)
                server.sendmail(settings.gmail_user, settings.gmail_user, msg.as_string())

            logger.info("Deal submission sent", company=company_name)
            return {"success": True}
        except Exception as e:
            logger.error("Error in /api/submit_deal", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to send deal submission")

    return app
