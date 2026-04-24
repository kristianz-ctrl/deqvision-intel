"""
DEQvision Intelligence Platform — Backend
Powered by Google Gemini AI | 10-Agent Simulation Engine
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app, origins="*")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

AGENTS = [
    {"id": "KM", "name": "Клиент М.", "role": "loyal_customer", "label": "лоялен", "color": "green"},
    {"id": "SK", "name": "Скептик К.", "role": "skeptic", "label": "скептичен", "color": "red"},
    {"id": "AT", "name": "Лоялен Т.", "role": "advocate", "label": "поддържа", "color": "green"},
    {"id": "RB", "name": "Изследовател Б.", "role": "researcher", "label": "наблюдава", "color": "gray"},
    {"id": "AP", "name": "Адвокат П.", "role": "promoter", "label": "промотира", "color": "green"},
    {"id": "MN", "name": "Неутрален Н.", "role": "neutral", "label": "неутрален", "color": "gray"},
    {"id": "IH", "name": "Инфлуенсър И.", "role": "influencer", "label": "усилва", "color": "yellow"},
    {"id": "VO", "name": "Стойност О.", "role": "value_seeker", "label": "скептичен", "color": "red"},
    {"id": "RA", "name": "Ранен А.", "role": "early_adopter", "label": "купува рано", "color": "green"},
    {"id": "DS", "name": "Оферта Д.", "role": "deal_seeker", "label": "изчаква", "color": "gray"},
]

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "DEQvision Intelligence Platform — Online", "agents": 10})

@app.route("/api/simulate", methods=["POST"])
def simulate():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key not configured"}), 500

    data = request.get_json() or {}
    client = data.get("client", "")
    product = data.get("product", "")
    hypothesis = data.get("hypothesis", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")
    context = data.get("context", "")

    model = genai.GenerativeModel("gemini-2.0-flash")

    results = []
    for agent in AGENTS:
        prompt = f"""You are simulating a market research agent for a Bulgarian marketing agency called DEQvision.

Agent Profile:
- Name: {agent['name']}
- Role: {agent['role']}
- Behavioral tendency: {agent['label']}

Research Brief:
- Client: {client}
- Product/Service: {product}
- Target Audience: {audience}
- Hypothesis: {hypothesis}
- Research Goal: {goal}
- Additional Context: {context}

Respond as this specific agent type would react to this product/message. Be realistic and specific.
Provide:
1. Initial reaction (1-2 sentences)
2. Key concern or positive (1 sentence)
3. Likely behavior (buy/ignore/share/complain) with brief reason
4. Sentiment score: positive/neutral/negative

Respond in Bulgarian language. Keep it concise."""

        try:
            response = model.generate_content(prompt)
            results.append({
                "agent": agent,
                "response": response.text,
                "status": "complete"
            })
        except Exception as e:
            results.append({
                "agent": agent,
                "response": f"Грешка: {str(e)}",
                "status": "error"
            })

    # Generate summary
    summary_prompt = f"""Based on these 10 agent responses for a market research simulation, provide a strategic summary in Bulgarian.

Product: {product}
Hypothesis: {hypothesis}

Agent responses:
{json.dumps([r['response'] for r in results], ensure_ascii=False)}

Provide:
1. Overall sentiment breakdown (% positive/neutral/negative)
2. Top 3 insights
3. Hypothesis verdict (validated/rejected/partially validated)
4. Recommended action

Keep it concise and actionable. In Bulgarian."""

    try:
        summary_response = model.generate_content(summary_prompt)
        summary = summary_response.text
    except Exception as e:
        summary = f"Summary error: {str(e)}"

    return jsonify({
        "success": True,
        "agents": results,
        "summary": summary,
        "brief": {
            "client": client,
            "product": product,
            "hypothesis": hypothesis,
            "goal": goal
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
