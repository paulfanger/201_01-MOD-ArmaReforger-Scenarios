"""
Arma Reforger Mission Authoring Backend
========================================

Entry point. FastAPI app + route registration.

The backend is PURE LOGIC: asset validation, file generation, snapshot management.
LLM-calls happen in Claude Code subagents, NOT here. This keeps the backend
provider-agnostic and testable in isolation.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown hooks."""
    # Startup: load asset catalog into memory, init SQLite if needed
    # TODO (Sonnet 4.6): wire up catalog + snapshot DB
    yield
    # Shutdown: close DB connections


app = FastAPI(
    title="Arma Reforger Mission Authoring Backend",
    description="Pure-logic backend for AI-native mission authoring",
    version="0.1.0-mvp",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    """Liveness probe — used by pipeline-tester pre-check."""
    return {"status": "ok", "service": "reforger-mission-backend", "version": "0.1.0-mvp"}


from backend.routes import revisions as revisions_router

app.include_router(revisions_router.router, prefix="/missions", tags=["revisions"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
