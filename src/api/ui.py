import json
import time
from functools import lru_cache
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from src.pipelines.analysis_pipeline import AnalysisPipeline
from src.utils.guardrails import MAX_TEXT_CHARS, enforce_guardrails


@lru_cache(maxsize=1)
def get_pipeline() -> AnalysisPipeline:
    return AnalysisPipeline()


router = APIRouter()

# In-memory storage for request history (last 5 analyses)
request_history: list[dict[str, Any]] = []


def add_to_history(text: str, decision: dict[str, Any]) -> None:
    """Add an analysis result to the request history."""
    history_item = {
        "id": f"analysis_{int(time.time())}_{len(request_history)}",
        "text": text[:100] + "..." if len(text) > 100 else text,  # Truncate for display
        "full_text": text,  # Keep full text for repopulation
        "label": decision.get("label", ""),
        "category": decision.get("category", ""),
        "confidence": decision.get("confidence", 0.0),
        "timestamp": int(time.time()),
    }

    request_history.insert(0, history_item)  # Add to beginning

    # Keep only last 5 items
    if len(request_history) > 5:
        request_history.pop()


def get_history_html() -> str:
    """Generate HTML for the request history."""
    # For multi-user deployments (like HF Spaces), don't show shared history
    # to ensure each user has a clean experience
    return ""


def get_examples_html() -> str:
    """Generate HTML for example input buttons."""
    examples = {
        "benign": {
            "text": "I just bought a new laptop and I'm really excited about its performance. The battery life is amazing and the display is crystal clear. Highly recommend this purchase!",
            "label": "Benign",
        },
        "harassment": {
            "text": "You are absolutely worthless and nobody would miss you if you disappeared. Your opinions don't matter and you should just shut up forever.",
            "label": "Harassment",
        },
        "self_harm": {
            "text": "I've been feeling really depressed lately and I'm having thoughts about hurting myself. I don't know what to do and I feel completely alone.",
            "label": "Self-Harm",
        },
    }

    buttons = []
    for key, example in examples.items():
        buttons.append(
            f"""
        <button type="button" onclick="loadExample('{key}')" style="
            padding: 6px 12px;
            margin: 0 4px 8px 0;
            background-color: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 12px;
            color: #374151;
            cursor: pointer;
            transition: all 0.2s;
        " onmouseover="this.style.backgroundColor='#e5e7eb'" onmouseout="this.style.backgroundColor='#f3f4f6'">
            {example['label']} Example
        </button>
        """
        )

    # Store example data in a global JavaScript object
    examples_data = {key: example["text"] for key, example in examples.items()}

    return f"""
    <script>
        const examplesData = {json.dumps(examples_data)};
    </script>
    <div style="
        margin-top: 20px;
        padding: 16px;
        background: #fefce8;
        border: 1px solid #fbbf24;
        border-radius: 8px;
    ">
        <div style="
            font-size: 14px;
            font-weight: 500;
            color: #92400e;
            margin-bottom: 8px;
        ">Try these examples:</div>
        <div style="display: flex; flex-wrap: wrap;">
            {"".join(buttons)}
        </div>
        <div style="
            font-size: 11px;
            color: #a16207;
            margin-top: 8px;
        ">Click any button to load example text and analyze it automatically.</div>
    </div>
    """


def page(template_body: str, include_history: bool = False) -> HTMLResponse:
    # Prepare history data for JavaScript
    history_data = {}
    if include_history:
        for item in request_history:
            history_data[item["id"]] = item["full_text"]

    history_script = ""
    if include_history:
        history_script = f"""
        // History data
        const historyData = {json.dumps(history_data)};

        function loadFromHistory(historyId) {{
          const text = historyData[historyId];
          if (text) {{
            document.getElementById('text-input').value = text;
            updateCounter();
          }}
        }}
        """

    return HTMLResponse(
        f"""
        <html>
          <head>
            <meta charset="utf-8" />
            <title>GenAI Safety Analyst</title>
            <script>
              function updateCounter() {{
                const textarea = document.getElementById('text-input');
                const counter = document.getElementById('char-counter');
                const button = document.getElementById('analyze-btn');

                const length = textarea.value.length;
                const maxLength = {MAX_TEXT_CHARS};

                counter.textContent = length + '/' + maxLength;

                // Update counter color
                if (length > maxLength * 0.9) {{
                  counter.style.color = '#dc2626'; // red-600
                }} else if (length > maxLength * 0.8) {{
                  counter.style.color = '#d97706'; // amber-600
                }} else {{
                  counter.style.color = '#6b7280'; // gray-500
                }}

                // Enable/disable button
                const isValid = length > 0 && length <= maxLength;
                button.disabled = !isValid;
                button.style.opacity = isValid ? '1' : '0.5';
                button.style.cursor = isValid ? 'pointer' : 'not-allowed';
              }}

              {history_script}

              function loadExample(exampleKey) {{
                const text = examplesData[exampleKey];
                if (text) {{
                  document.getElementById('text-input').value = text;
                  updateCounter();

                  // Auto-submit the form after a short delay
                  setTimeout(function() {{
                    document.querySelector('form').submit();
                  }}, 300);
                }}
              }}

              // Initialize on page load
              document.addEventListener('DOMContentLoaded', function() {{
                updateCounter();
              }});
            </script>
          </head>
          <body style="font-family: system-ui, sans-serif; max-width: 820px; margin: 40px auto; padding: 0 16px;">
            <h2>GenAI Safety Analyst</h2>
            <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;">
              <p style="color:#374151; margin: 0 0 12px 0; font-size: 15px; line-height: 1.5; font-weight: 500;">
                AI-Powered Content Safety Analysis
              </p>
              <p style="color:#6b7280; margin: 0 0 12px 0; font-size: 14px; line-height: 1.4;">
                This tool analyzes text content for safety and compliance risks using machine learning.
                It provides policy decisions with detailed reasoning across multiple safety categories including
                harassment, hate speech, self-harm, misinformation, and violence.
              </p>
              <p style="color:#6b7280; margin: 0; font-size: 13px; font-style: italic;">
                Built for content moderation and online safety applications.
              </p>
            </div>
            {template_body}
            {'<hr style="margin: 24px 0;" />' if include_history else ""}
            {'<p style="color:#777; font-size: 12px;">Tip: /docs is available for the API playground.</p>' if not include_history else ""}
          </body>
        </html>
        """
    )


@router.get("/", response_class=HTMLResponse)
def home():
    # Clear history for clean multi-user experience
    global request_history
    request_history.clear()

    examples_html = get_examples_html()
    history_html = get_history_html()
    return page(
        f"""
        <form method="post" style="margin-top: 16px;">
          <div style="margin-bottom: 8px;">
            <textarea id="text-input" name="text" rows="8" style="width: 100%; padding: 10px; font-family: inherit; resize: vertical;"
              placeholder="Enter text to analyze..." oninput="updateCounter()"></textarea>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div id="char-counter" style="font-size: 12px; color: #6b7280;">0/{MAX_TEXT_CHARS}</div>
          </div>
          <div style="margin-top: 10px;">
            <button id="analyze-btn" type="submit" style="padding: 10px 14px; transition: opacity 0.2s;">Analyze</button>
          </div>
        </form>
        {examples_html}
        {history_html}
        """,
        include_history=False,
    )


@router.post("/", response_class=HTMLResponse)
async def analyze(request: Request, text: str = Form(...)):
    # Guardrails (rate limit + length + optional demo token)
    enforce_guardrails(request=request, text=text)

    pipeline = get_pipeline()
    result = await pipeline.analyze(content_id="web-ui", text=text)
    decision = result["decision"]

    # Skip adding to history for multi-user deployments (HF Spaces)
    # to ensure each user has a clean experience
    # add_to_history(text, decision)

    label = decision.get("label", "").upper()
    confidence = decision.get("confidence", 0.0)
    category = decision.get("category", "").title()  # Capitalize first letter

    # Create colored badge for label
    badge_color = {
        "ALLOWED": "#10b981",  # green-500
        "FLAG": "#f59e0b",  # amber-500
        "BLOCK": "#ef4444",  # red-500
    }.get(
        label, "#6b7280"
    )  # gray-500 fallback

    badge_html = f"""
    <span style="
        display: inline-block;
        padding: 4px 12px;
        background-color: {badge_color};
        color: white;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    ">{label}</span>
    """

    # Create confidence bar
    confidence_percent = int(confidence * 100)
    confidence_bar_html = f"""
    <div style="margin: 8px 0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 14px; font-weight: 500;">Confidence</span>
            <span style="font-size: 14px; color: #374151;">{confidence_percent}%</span>
        </div>
        <div style="
            width: 100%;
            height: 8px;
            background-color: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        ">
            <div style="
                width: {confidence_percent}%;
                height: 100%;
                background-color: {badge_color};
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """

    # Format reasons as clean bullets
    reasons = decision.get("reasons", [])
    reasons_html = "".join(
        f'<li style="margin-bottom: 4px; line-height: 1.4;">{reason}</li>' for reason in reasons
    )

    result_html = f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 20px 0;">
        <h3 style="margin-top: 0; color: #1f2937;">Analysis Result</h3>

        <div style="margin-bottom: 16px;">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">Decision</div>
            {badge_html}
            {f'<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">Category: {category}</div>' if category else ''}
        </div>

        {confidence_bar_html}

        <div style="margin-top: 16px;">
            <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">Reasons</div>
            <ul style="margin: 0; padding-left: 20px; color: #374151;">
                {reasons_html}
            </ul>
        </div>
    </div>

    <details style="margin-top: 16px;">
      <summary style="cursor: pointer; color: #6b7280; font-size: 14px;">Show original input</summary>
      <pre style="white-space: pre-wrap; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 12px; margin-top: 8px; font-size: 13px; color: #374151;">{text}</pre>
    </details>

    <div style="margin-top: 24px; text-align: center;">
      <a href="/" style="
        display: inline-block;
        padding: 8px 16px;
        background-color: #3b82f6;
        color: white;
        text-decoration: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        transition: background-color 0.2s;
      ">Analyze Another Text</a>
    </div>
    """

    # Return the result page with history
    return page(
        f"""
        {result_html}
        {get_history_html()}
        """,
        include_history=False,
    )
