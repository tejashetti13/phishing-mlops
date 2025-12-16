# api/app.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.inference import predict_url

def apply_protocol_rule(url: str, prob: float) -> float:
    """
    Soft rule-based adjustment:
    - HTTPS reduces phishing risk slightly
    - HTTP increases phishing risk slightly
    """
    url = url.lower()

    if url.startswith("https://"):
        prob = prob * 0.4          # safer, not always safe
    elif url.startswith("http://"):
        prob = min(prob * 1.3, 1)  # riskier, cap at 1

    return prob

# FastAPI app
app = FastAPI(
    title="Phishing URL Detection API",
    description="API + Simple UI to predict whether a given URL is phishing or legitimate.",
    version="1.0.0",
)


# --------- Pydantic model for API ----------

class UrlRequest(BaseModel):
    url: str


# --------- Simple Web UI (Home Page) ----------

@app.get("/", response_class=HTMLResponse)
def home():
    """
    Simple HTML page with one input and a button.
    Uses JavaScript to call the /predict API and show result.
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <title>Phishing URL Detector</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background: #ffffff;
                padding: 24px 28px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                max-width: 480px;
                width: 100%;
            }
            h1 {
                font-size: 22px;
                margin-bottom: 8px;
                text-align: center;
            }
            p.subtitle {
                font-size: 13px;
                color: #666;
                margin-top: 0;
                margin-bottom: 16px;
                text-align: center;
            }
            label {
                font-size: 14px;
                font-weight: 600;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px 12px;
                margin-top: 6px;
                margin-bottom: 14px;
                border-radius: 8px;
                border: 1px solid #ccc;
                font-size: 14px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
                background: #2563eb;
                color: #ffffff;
            }
            button:disabled {
                opacity: 0.7;
                cursor: not-allowed;
            }
            .result {
                margin-top: 16px;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
                display: none;
            }
            .result.safe {
                background: #ecfdf3;
                color: #166534;
                border: 1px solid #bbf7d0;
            }
            .result.phishing {
                background: #fef2f2;
                color: #991b1b;
                border: 1px solid #fecaca;
            }
            .result .label {
                font-weight: 700;
                font-size: 15px;
            }
            .prob {
                font-size: 13px;
                margin-top: 6px;
            }
            .error {
                color: #b91c1c;
                font-size: 13px;
                margin-top: 8px;
            }
            .footer {
                margin-top: 16px;
                font-size: 11px;
                text-align: center;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Phishing URL Detector</h1>
            <p class="subtitle">Paste any URL and check if it looks suspicious.</p>

            <label for="url-input">URL</label>
            <input
                type="text"
                id="url-input"
                placeholder="https://example.com/login"
            />

            <button id="check-btn" onclick="checkUrl()">Check URL</button>

            <div id="result" class="result">
                <div class="label" id="result-label"></div>
                <div class="prob" id="result-prob"></div>
            </div>

            <div id="error" class="error"></div>

            <div class="footer">
                Backend: FastAPI · Model: Random Forest
            </div>
        </div>

        <script>
            async function checkUrl() {
                const input = document.getElementById('url-input');
                const btn = document.getElementById('check-btn');
                const resultBox = document.getElementById('result');
                const resultLabel = document.getElementById('result-label');
                const resultProb = document.getElementById('result-prob');
                const errorBox = document.getElementById('error');

                const url = input.value.trim();
                errorBox.textContent = '';
                resultBox.style.display = 'none';
                resultBox.className = 'result';

                if (!url) {
                    errorBox.textContent = 'Please enter a URL.';
                    return;
                }

                btn.disabled = true;
                btn.textContent = 'Checking...';

                try {
                    const response = await fetch('/predict', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify({ url })
                    });

                    if (!response.ok) {
                        throw new Error('Server error: ' + response.status);
                    }

                    const data = await response.json();

                    const label = data.prediction; // "phishing" or "legitimate"
                    const prob = data.probability_phishing;

                    if (label === 'phishing') {
                        resultBox.classList.add('phishing');
                        resultLabel.textContent = '🚨 Phishing URL detected';
                    } else {
                        resultBox.classList.add('safe');
                        resultLabel.textContent = '✅ Looks legitimate';
                    }

                    resultProb.textContent = `Model confidence (phishing): ${(prob * 100).toFixed(2)}%`;
                    resultBox.style.display = 'block';

                } catch (err) {
                    errorBox.textContent = 'Error: ' + err.message;
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Check URL';
                }
            }
        </script>
    </body>
    </html>
    """


# --------- Existing JSON API Endpoints ----------

@app.get("/health")
def health():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}


@app.post("/predict")
def predict(request: UrlRequest):
    """
    Predict if the given URL is phishing or legitimate.
    """
    raw_label, raw_prob = predict_url(request.url)

    # Apply soft protocol rule
    final_prob = apply_protocol_rule(request.url, raw_prob)

    # Final decision threshold
    final_label = 1 if final_prob >= 0.6 else 0

    return {
        "url": request.url,
        "label": final_label,
        "prediction": "phishing" if final_label == 1 else "legitimate",
        "probability_phishing": round(final_prob, 4),
        "model_probability": round(raw_prob, 4),
    }

