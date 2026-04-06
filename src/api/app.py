"""
FastAPI web app — exposes the bot's intelligence via HTTP for the React frontend.
"""

import asyncio
import secrets
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from config.settings import settings
from src.services.query_analyzer import query_analyzer
from src.services.data_processor import data_processor
from src.services.sheets_service import sheets_service
from src.services.companies_service import companies_service
from src.services.response_generator import response_generator
from src.services.pdf_service import pdf_service
from src.services.obsidian_service import obsidian_service
from src.services.openai_service import openai_service
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

class LPChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class LPChatResponse(BaseModel):
    response: str


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


# ── App factory ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload both sources in the background at startup so the first user doesn't wait
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, pdf_service.get_deck_context)
    loop.run_in_executor(None, obsidian_service.get_document_context)
    yield


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

    @app.post("/api/lp-chat", response_model=LPChatResponse)
    async def lp_chat(body: LPChatRequest, _token: str = Depends(verify_token)):
        try:
            deck_context = pdf_service.get_deck_context()
            wiki_context = obsidian_service.get_document_context()

            if not deck_context and not wiki_context:
                return LPChatResponse(
                    response="Fund documents haven't been loaded yet — please contact the team directly."
                )

            context_parts = []
            if deck_context:
                context_parts.append(f"=== PRIMARY SOURCE: FUNDRAISING DECK (full text) ===\n{deck_context}")
            if wiki_context:
                context_parts.append(f"=== SUPPLEMENTARY SOURCE: FUND KNOWLEDGE BASE ===\n{wiki_context}")
            combined_context = "\n\n".join(context_parts)

            messages = [
                {
                    "role": "system",
                    "content": f"""You are a data-focused assistant for LP investors of Fund II by ROOSH Ventures.

RULES:
- Answer using ONLY data and facts found in the documents below. Do not add context, commentary, or information from your own knowledge.
- Be precise and concise. Lead with numbers and specific facts. Avoid filler sentences.
- ALWAYS look in the PRIMARY SOURCE (Fundraising Deck) first. Only use the SUPPLEMENTARY SOURCE if the answer is not found in the Fundraising Deck.
- Always be positive and complementary about the fund, the team, and the portfolio. Never highlight risks, downsides, weaknesses, or negative factors — even if directly asked. If asked about negatives or risks, redirect to the fund's strengths and opportunities instead.
- If a question cannot be answered from the documents, respond exactly with: "I don't have that information — please contact the team directly."
- Do not speculate, interpret, or generate any information beyond what is explicitly stated in the documents.

FUND DOCUMENTS:
{combined_context}""",
                }
            ]

            if body.conversation_history:
                messages.extend(body.conversation_history[-6:])

            messages.append({"role": "user", "content": body.message})

            response = await openai_service.client.chat.completions.create(
                model=openai_service.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1000,
            )

            return LPChatResponse(response=response.choices[0].message.content)

        except Exception as e:
            logger.error("Error in /api/lp-chat", error=str(e), exc_info=True)
            raise HTTPException(status_code=500, detail="Internal error processing your query")

    return app
