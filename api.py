"""FastAPI entry points for the Cred support agent."""

from pathlib import Path
from typing import Any

import json
import time

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from agent_graph import build_agent
from guardrails import PromptInjectionError, UngroundedResponseError
from request_logging import write_request_log


app = FastAPI(title="Cred Domain Support Agent", version="1.0.0")
AGENT = build_agent()
KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"


@app.middleware("http")
async def structured_request_logging(request: Request, call_next):
    started_at = time.perf_counter()
    body = await request.body()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        try:
            request_text = json.loads(body.decode("utf-8")).get("query", body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            request_text = body.decode("utf-8", errors="replace")
        write_request_log(request.method, request.url.path, str(request_text), status_code, started_at)
    return response


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


class AskResponse(BaseModel):
    route: str
    answer: str
    details: dict[str, Any]


class AddDocumentRequest(BaseModel):
    filename: str = Field(pattern=r"^[A-Za-z0-9_-]+\.md$", min_length=4, max_length=100)
    content: str = Field(min_length=2, max_length=20_000)


class AddDocumentResponse(BaseModel):
    filename: str
    message: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        response = AGENT.invoke({"query": request.query})["response"]
    except PromptInjectionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except UngroundedResponseError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return AskResponse(**response)


@app.post("/add-document", response_model=AddDocumentResponse)
def add_document(request: AddDocumentRequest) -> AddDocumentResponse:
    path = KNOWLEDGE_BASE_DIR / request.filename
    path.write_text(request.content, encoding="utf-8")
    return AddDocumentResponse(filename=request.filename, message="Document added")
