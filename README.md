# PromptShield

PromptShield is a resilient browser prompt enhancer for AI apps like ChatGPT, Claude, and Gemini.

It improves weak prompts and demonstrates resilience when the primary LLM or tool layer fails. The MVP uses a Chrome extension frontend, FastAPI backend, and a TrueFoundry AI Gateway-compatible OpenAI client.

## What it does

- Floats over ChatGPT / Claude / Gemini
- Reads the user's draft prompt
- Enhances it based on mode: general, resume, coding, research, academic
- Calls a backend connected to TrueFoundry AI Gateway
- Falls back to a local rule-based prompt enhancer if the gateway/model fails
- Includes chaos mode for hackathon demo: simulate LLM failure
- Logs gateway success/failure and fallback behavior

## Architecture

```txt
Browser AI App
   ↓
PromptShield Chrome Extension
   ↓ localhost:8000
FastAPI Backend
   ↓
TrueFoundry AI Gateway Virtual Model
   ↓
Primary LLM → fallback model(s)

If gateway/model fails:
FastAPI → local fallback enhancer → user still gets a useful prompt
```

## Repo structure

```txt
promptshield/
  backend/
    main.py
    gateway_client.py
    resilience.py
    prompt_templates.py
    requirements.txt
    .env.example
  extension/
    manifest.json
    content.js
    styles.css
  README.md
```

## Prerequisites

- Python 3.10+
- Google Chrome or Chromium-based browser
- TrueFoundry AI Gateway endpoint and API key

You can still run the app without TrueFoundry credentials to test local fallback behavior.

## 1. Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```bash
TRUEFOUNDRY_API_KEY=your_truefoundry_gateway_key
TRUEFOUNDRY_GATEWAY_BASE_URL=https://your-gateway-url/v1
TRUEFOUNDRY_VIRTUAL_MODEL=promptshield-router
```

Start the server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```txt
http://localhost:8000/docs
```

## 2. Test the backend directly

```bash
curl -X POST http://localhost:8000/enhance \
  -H "Content-Type: application/json" \
  -d '{"prompt":"make my resume better","mode":"resume"}'
```

Simulate LLM failure:

```bash
curl -X POST "http://localhost:8000/chaos/toggle?kind=llm_failure&enabled=true"
```

Turn it off:

```bash
curl -X POST "http://localhost:8000/chaos/toggle?kind=llm_failure&enabled=false"
```

View logs:

```bash
curl http://localhost:8000/logs
```

## 3. Load the Chrome extension

1. Open Chrome.
2. Go to `chrome://extensions/`.
3. Turn on **Developer mode**.
4. Click **Load unpacked**.
5. Select the `extension/` folder.
6. Open `https://chatgpt.com/`.
7. You should see the PromptShield floating widget.

## 4. Demo script

1. Open ChatGPT.
2. Type: `make my resume better`.
3. Click **Enhance Prompt**.
4. Show the improved prompt.
5. Click **Simulate LLM Failure**.
6. Type another weak prompt.
7. Click **Enhance Prompt** again.
8. Show that PromptShield still returns a useful prompt using local fallback.
9. Open `http://localhost:8000/logs` to show resilience logs.

## Hackathon positioning

**PromptShield: A resilient prompt copilot that improves user input and survives LLM/tool failures without breaking the user experience.**

Failure scenarios shown:

- Primary LLM failure
- Gateway/client exception
- Slow response simulation
- Local fallback response
- User-facing recovery status
- Observability logs

## Future improvements

- Add MCP server failure simulation
- Add provider-level fallback visualization
- Add prompt quality scoring
- Add user memory/preferences
- Add team prompt library
- Add SDK for agent builders
