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


# Route modules will be wired in by Sonnet 4.6 after research/02-mission-format.md is final:
#
# from routes import catalog, missions, snapshots, exporters
# app.include_router(catalog.router, prefix="/catalog", tags=["catalog"])
# app.include_router(missions.router, prefix="/missions", tags=["missions"])
# app.include_router(snapshots.router, prefix="/snapshots", tags=["snapshots"])
# app.include_router(exporters.router, prefix="/exporters", tags=["exporters"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
