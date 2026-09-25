from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from backend.model import FlirtGPT
except ModuleNotFoundError:  # `uvicorn main:app` when the current directory is backend/
    from model import FlirtGPT

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("flirtgpt.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.flirtgpt = FlirtGPT()
    yield


app = FastAPI(title="FlirtGPT API", docs_url=None, redoc_url=None, lifespan=lifespan)
origins = [origin.strip() for origin in os.getenv("FLIRTGPT_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,https://gpt-from-scratch-one.vercel.app").split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class Message(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[Message] = Field(default_factory=list, max_length=40)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(payload: ChatRequest, request: Request):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")
    history = [item.model_dump() for item in payload.history]
    # Accept only a properly alternating conversation ending in a user turn.
    conversation = history + [{"role": "user", "content": message}]
    if any(item["role"] == conversation[index - 1]["role"] for index, item in enumerate(conversation) if index):
        raise HTTPException(status_code=422, detail="Conversation history is invalid.")
    if conversation[-1]["role"] != "user":
        raise HTTPException(status_code=422, detail="Conversation history must end with a user message.")
    try:
        response = request.app.state.flirtgpt.respond(conversation)
        if not response:
            raise RuntimeError("The model returned an empty response.")
        return {"response": response}
    except HTTPException:
        raise
    except Exception:
        LOGGER.exception("FlirtGPT generation failed")
        raise HTTPException(status_code=500, detail="FlirtGPT could not generate a response.") from None
