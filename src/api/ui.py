from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse

from src.pipelines.analysis_pipeline import AnalysisPipeline
from src.utils.guardrails import enforce_guardrails

router = APIRouter()
pipeline = AnalysisPipeline()


def page(template_body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""
        <html>
          <head>
            <meta charset="utf-8" />
            <title>GenAI Safety Analyst</title>
          </head>
          <body style="font-family: system-ui, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 16px;">
            <h2>GenAI Safety Analyst</h2>
            <p style="color:#555;">
              Paste text to analyze. You’ll get a policy decision (allowed/flag/block) with reasons.
            </p>
            {template_body}
            <hr style="margin: 24px 0;" />
            <p style="color:#777; font-size: 12px;">
              Tip: /docs is available for the API playground.
            </p>
          </body>
        </html>
        """
    )


@router.get("/", response_class=HTMLResponse)
def home():
    return page(
        """
        <form method="post" style="margin-top: 16px;">
          <textarea name="text" rows="8" style="width: 100%; padding: 10px;" placeholder="Enter text..."></textarea>
          <div style="margin-top: 10px;">
            <button type="submit" style="padding: 10px 14px;">Analyze</button>
          </div>
        </form>
        """
    )


@router.post("/", response_class=HTMLResponse)
async def analyze(request: Request, text: str = Form(...)):
    # Guardrails (rate limit + length + optional demo token)
    enforce_guardrails(request=request, text=text)

    result = await pipeline.analyze(content_id="web-ui", text=text)
    decision = result["decision"]

    reasons_html = "".join(f"<li>{r}</li>" for r in decision.get("reasons", []))

    return page(
        f"""
        <h3>Result</h3>
        <p><b>Label:</b> {decision.get("label")}</p>
        <p><b>Confidence:</b> {decision.get("confidence")}</p>
        <p><b>Reasons:</b></p>
        <ul>{reasons_html}</ul>

        <details style="margin-top: 12px;">
          <summary>Show input</summary>
          <pre style="white-space: pre-wrap; background: #f6f6f6; padding: 10px;">{text}</pre>
        </details>

        <div style="margin-top: 16px;">
          <a href="/">Analyze another</a>
        </div>
        """
    )
