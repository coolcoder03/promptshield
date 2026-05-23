from __future__ import annotations

import os
import time
import asyncio
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from prompt_templates import MODE_HINTS, SYSTEM_PROMPT
from resilience import add_log, chaos_state

load_dotenv()


def _client() -> AsyncOpenAI:
    api_key = os.getenv("TRUEFOUNDRY_API_KEY", "")
    base_url = os.getenv("TRUEFOUNDRY_GATEWAY_BASE_URL", "")

    if not api_key or not base_url:
        raise RuntimeError(
            "Missing TRUEFOUNDRY_API_KEY or TRUEFOUNDRY_GATEWAY_BASE_URL. "
            "Copy .env.example to .env and fill in your Gateway values."
        )

    return AsyncOpenAI(api_key=api_key, base_url=base_url)


async def enhance_prompt(prompt: str, mode: str = "general") -> dict[str, Any]:
    start = time.time()
    clean_prompt = prompt.strip()
    selected_mode = mode if mode in MODE_HINTS else "general"

    if not clean_prompt:
        return {
            "enhanced_prompt": "Please enter a prompt first.",
            "provider_status": "empty_prompt",
            "latency_ms": 0,
        }

    if chaos_state.get("slow_response"):
        add_log("chaos_slow_response", {"message": "Injected artificial latency."})
        await asyncio.sleep(2)

    if chaos_state.get("llm_failure"):
        add_log("chaos_llm_failure", {"message": "Simulated LLM failure; local fallback used."})
        return {
            "enhanced_prompt": fallback_enhance(clean_prompt, selected_mode),
            "provider_status": "local_fallback",
            "failure_reason": "simulated_llm_failure",
            "latency_ms": int((time.time() - start) * 1000),
        }

    try:
        client = _client()
        model = os.getenv("TRUEFOUNDRY_VIRTUAL_MODEL", "promptshield-router")

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Mode: {selected_mode}\n"
                        f"Mode guidance: {MODE_HINTS[selected_mode]}\n\n"
                        f"User prompt:\n{clean_prompt}"
                    ),
                },
            ],
            temperature=0.3,
        )

        enhanced = response.choices[0].message.content or fallback_enhance(clean_prompt, selected_mode)
        add_log(
            "gateway_success",
            {
                "model": model,
                "mode": selected_mode,
                "latency_ms": int((time.time() - start) * 1000),
            },
        )

        return {
            "enhanced_prompt": enhanced,
            "provider_status": "gateway_success",
            "model": model,
            "latency_ms": int((time.time() - start) * 1000),
        }

    except Exception as exc:
        add_log("gateway_error_local_fallback", {"error": str(exc), "mode": selected_mode})
        return {
            "enhanced_prompt": fallback_enhance(clean_prompt, selected_mode),
            "provider_status": "local_fallback",
            "failure_reason": str(exc),
            "latency_ms": int((time.time() - start) * 1000),
        }


def fallback_enhance(prompt: str, mode: str = "general") -> str:
    if mode == "resume":
        return f"""Enhanced Prompt:
Act as a senior technical recruiter and ATS resume expert. Review and improve the following resume-related request:

{prompt}

Please provide:
1. A stronger ATS-friendly version
2. Missing keywords for the target role
3. Weak bullet rewrites using measurable impact
4. A concise final version ready to use

Why this is better:
- It defines the expert role and expected output.
- It asks for recruiter, ATS, and impact-focused improvements.

Optional Variations:
1. Make this resume bullet stronger for an ML Engineer role.
2. Rewrite my resume summary for AI/ML roles using measurable impact.
"""

    if mode == "coding":
        return f"""Enhanced Prompt:
Act as a senior software engineer. Help me solve the following coding task:

{prompt}

Please include:
1. Problem interpretation
2. Edge cases
3. Step-by-step approach
4. Clean code
5. Time and space complexity
6. Test cases

Why this is better:
- It asks for both reasoning and implementation.
- It includes edge cases, complexity, and tests.

Optional Variations:
1. Solve this in Python with explanation.
2. Optimize this solution and explain trade-offs.
"""

    return f"""Enhanced Prompt:
Act as an expert assistant. Help me with the following task:

{prompt}

Please structure your answer with:
1. Clear assumptions
2. Step-by-step guidance
3. Practical examples
4. Common mistakes to avoid
5. A final actionable recommendation

Why this is better:
- It clarifies the role, structure, and expected depth.
- It turns a vague request into an actionable instruction.

Optional Variations:
1. Give me a concise answer with examples.
2. Give me a detailed plan with milestones and risks.
"""
