# AI-Assisted FastAPI Service

A production-ready FastAPI backend service that ingests unstructured customer feedback, passes it to an LLM API (OpenAI or Gemini via an interchangeable service layer), and returns strictly validated JSON.

## Features
- **Interchangeable LLM Layer**: Swap between OpenAI and Gemini by changing an environment variable.
- **Strict JSON Output Validation**: Uses Pydantic to ensure the LLM output conforms perfectly to expected structures.
- **Custom Rate Limiting**: In-memory sliding window rate limiting for endpoints.
- **Latency Logging**: Middleware for logging request processing time.
- **Robust Error Handling**: Graceful fallback and error reporting on LLM failures or parsing issues.

## Setup Instructions

1. **Clone the repository and navigate to the directory**:
   ```bash
   cd AI-Assisted-FastAPI-Service
   ```

2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   *Required variables*:
   - `OPENAI_API_KEY` (if using OpenAI)
   - `GEMINI_API_KEY` (if using Gemini)
   - `LLM_PROVIDER` (set to `openai` or `gemini`)

5. **Run the server**:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation
Once the server is running, you can access the interactive Swagger UI documentation at:
http://127.0.0.1:8000/docs

## Examples

### cURL Request
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "feedback_text": "The new dashboard is incredibly fast and I love the dark mode feature. However, I could not find the export button where it used to be. It took me 10 minutes of searching. Please fix the navigation!",
  "source_platform": "Support Portal",
  "customer_id": "cust_828392"
}'
```

### Expected Response
```json
{
  "sentiment": "NEUTRAL",
  "summary": "Customer praises the fast dashboard and dark mode but is frustrated by the relocated export button and poor navigation.",
  "urgency_score": 3,
  "action_items": [
    "Make the export button more discoverable",
    "Review and improve overall navigation"
  ]
}
```

## Deployment Tips
- Use **Gunicorn** with **Uvicorn workers** in production:
  `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker`
- For persistent rate limiting in production (e.g. across multiple workers), consider swapping the custom in-memory rate limiter for a Redis-based solution.
- Store sensitive keys securely (e.g., AWS Secrets Manager, GitHub Secrets) and never commit the `.env` file.