"""FastAPI server exposing the ADK agent over AG-UI."""

import os

from ag_ui_adk import add_adk_fastapi_endpoint
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .adk_agent import create_agent, get_agent_metadata

load_dotenv()


def create_app() -> FastAPI:
    app = FastAPI(title="Amy Agent Core")
    cors_origins = os.getenv(
        "AGENT_CORE_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    adk_agent = create_agent()

    add_adk_fastapi_endpoint(app, adk_agent, path="/")

    @app.get("/agents")
    async def agents() -> dict[str, list[dict[str, str]]]:
        return {"agents": [get_agent_metadata()]}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def main() -> None:
    import uvicorn

    host = os.getenv("AGENT_CORE_HOST", "127.0.0.1")
    port = int(os.getenv("AGENT_CORE_PORT", "8000"))
    uvicorn.run("agent_core.server:create_app", host=host, port=port, factory=True)


if __name__ == "__main__":
    main()
