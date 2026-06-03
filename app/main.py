from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .api import TemanUmkmClient
from .session import AgentSessionStore, ClientFactory

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger("teman_umkm_ai")
logger.setLevel(logging.INFO)
logger.info("Logger initialized")

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    reply: str


def create_app(
    client_factory: ClientFactory = TemanUmkmClient,
    auto_login: bool = True,
) -> FastAPI:
    app = FastAPI(title="Teman UMKM AI")
    session_store = AgentSessionStore(
        client_factory=client_factory,
        auto_login=auto_login,
    )

    logger.info("Teman UMKM AI started")

    @app.get("/health")
    def health() -> dict[str, str]:
        logger.info("Health endpoint called")
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    def chat(request: ChatRequest) -> ChatResponse:
        logger.info("chat endpoint called")
        agent = session_store.get_agent(request.session_id)
        reply = agent.process(request.message)
        return ChatResponse(session_id=request.session_id, reply=reply)

    return app


app = create_app()
