from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from gateway_client import enhance_prompt
from resilience import add_log, chaos_state, logs

app = FastAPI(title="PromptShield API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The user's original prompt.")
    mode: str = Field("general", description="general, resume, coding, research, academic")


@app.get("/")
async def root():
    return {
        "name": "PromptShield",
        "message": "Resilient prompt enhancer API is running.",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "chaos_state": chaos_state}


@app.post("/enhance")
async def enhance(req: PromptRequest):
    return await enhance_prompt(req.prompt, req.mode)


@app.post("/chaos/toggle")
async def toggle_chaos(
    kind: str = Query(..., description="llm_failure, mcp_failure, or slow_response"),
    enabled: bool = Query(...),
):
    if kind not in chaos_state:
        return {"error": f"Unknown chaos kind: {kind}", "allowed": list(chaos_state.keys())}

    chaos_state[kind] = enabled
    add_log("chaos_toggle", {"kind": kind, "enabled": enabled})
    return {"kind": kind, "enabled": enabled, "chaos_state": chaos_state}


@app.get("/logs")
async def get_logs():
    return {"logs": logs[-30:]}
