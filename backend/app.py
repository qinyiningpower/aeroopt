# app.py


from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import os
import json

from datetime import datetime


from prompts import SYSTEM_PROMPT, get_analysis_prompt, get_zone_explanation_prompt, get_pressure_explanation_prompt, get_shape_explanation_prompt , get_drag_explanation_prompt, get_chat_prompt
from data_loader import data_loader


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


app = Flask(__name__)


CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5000"])


API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=API_KEY, timeout=30, max_retries=1) if API_KEY else None
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
AI_ROUTES = {"/analyze", "/explain_zone", "/explain_shape", "/explain_pressure", "/explain_drag", "/chat"}

@app.before_request
def prepare_request():
    if request.method == "OPTIONS":
        return None
    body = request.get_json(silent=True) if request.method == "POST" else {}
    if request.method == "POST" and not isinstance(body, dict):
        return jsonify(success=False, error="A JSON object is required"), 400
    model_id = request.headers.get("X-Model-ID") or body.get("model_id") or "model_01"
    if not isinstance(model_id, str) or not data_loader.load_model(model_id):
        return jsonify(success=False, error="Unknown model_id"), 404
    if request.path in AI_ROUTES:
        zone = body.get("zone_name")
        if request.path.startswith("/explain_") and zone not in {"front", "roof", "side", "rear"}:
            return jsonify(success=False, error="Unknown zone_name"), 400
        if request.path == "/chat" and (not isinstance(body.get("question"), str) or not body["question"].strip() or len(body["question"]) > 4000):
            return jsonify(success=False, error="question must contain 1 to 4000 characters"), 400
        if client is None:
            return jsonify(success=False, error="AI is disabled. Add OPENAI_API_KEY to backend/.env to enable explanations. Precomputed results remain available."), 503

@app.route("/")
def homepage():
    return send_from_directory(FRONTEND, "index.html")

@app.route("/<path:filename>")
def frontend_file(filename):
    return send_from_directory(FRONTEND, filename)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "AI Assistant is running",
        "model": MODEL,
        "ai_enabled": client is not None,
        "case_loaded": data_loader.is_data_loaded(),
        "current_model": data_loader.get_current_model_id()
    })


@app.route('/models', methods=['GET'])
def get_models():

    return jsonify({
        "success": True,
        "current_model": data_loader.get_current_model_id(),
        "available_models": data_loader.get_available_models()
    })


@app.route('/switch_model', methods=['POST'])
def switch_model():

    data = request.get_json()
    model_id = data.get('model_id')

    if not model_id:
        return jsonify({"success": False, "error": "model_id is required"}), 400

    print(f"Switching to model: {model_id}")

    success = data_loader.load_model(model_id)

    if success:

        print(f" Switched to: {data_loader.get_current_model_id()}")
        print(f" Drag: {data_loader.get_drag_before()} → {data_loader.get_drag_after()}")

        return jsonify({
            "success": True,
            "message": f"Switched to {model_id}",
            "case_info": {
                "case_id": data_loader.get_case_id(),
                "case_name": data_loader.get_case_name(),
                "drag_before": data_loader.get_drag_before(),
                "drag_after": data_loader.get_drag_after(),
                "reduction_percent": data_loader.get_drag_reduction_percent()
            },
            "current_model": data_loader.get_current_model_id()
        })
    else:
        return jsonify({"success": False, "error": f"Model {model_id} not found"}), 404


@app.route('/case_info', methods=['GET'])
def get_case_info():

    print(f"/case_info called, current model: {data_loader.get_current_model_id()}")

    return jsonify({
        "case_id": data_loader.get_case_id(),
        "case_name": data_loader.get_case_name(),
        "drag_before": data_loader.get_drag_before(),
        "drag_after": data_loader.get_drag_after(),
        "delta": data_loader.get_drag_delta(),
        "reduction_percent": data_loader.get_drag_reduction_percent(),
        "current_model": data_loader.get_current_model_id()
    })


@app.route('/shape_regions', methods=['GET'])
def get_shape_regions():
    return jsonify({
        "success": True,
        "data": data_loader.get_shape_regions()
    })


@app.route('/click_map', methods=['GET'])
def get_click_map():
    return jsonify({
        "success": True,
        "data": data_loader.get_click_map()
    })


@app.route('/pressure_regions', methods=['GET'])
def get_pressure_regions():
    return jsonify({
        "success": True,
        "data": data_loader.get_pressure_regions()
    })


@app.route('/analyze', methods=['POST'])
def analyze_pressure():
    data = request.get_json()


    image_before = data.get('image_before')
    image_after = data.get('image_after')


    if not image_before:
        image_before = data_loader.get_image_base64('before_pressure')
    if not image_after:
        image_after = data_loader.get_image_base64('after_pressure')


    if not image_before or not image_after:
        return jsonify({
            "success": False,
            "error": "No pressure field images provided. Please upload images or ensure images exist in project."
        }), 400


    drag_before = data_loader.get_drag_before()
    drag_after = data_loader.get_drag_after()

    reduction = ((drag_before - drag_after) / drag_before) * 100


    prompt = get_analysis_prompt(drag_before, drag_after)

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_before}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_after}"}}
                ]}
            ],
            max_tokens=800,
            temperature=0.4
        )

        explanation = response.choices[0].message.content

        return jsonify({
            "success": True,
            "explanation": explanation,
            "analysis": {
                "explanation": explanation
            },
            "drag": {
                "before": drag_before,
                "after": drag_after,
                "reduction_percent": round(reduction, 2)
            }
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "AI provider request failed. Check server configuration and retry."
        }), 500


@app.route('/explain_zone', methods=['POST'])
def explain_zone():
    data = request.get_json()
    zone_name = data.get('zone_name')
    user_question = data.get('question')

    if not zone_name:
        return jsonify({"success": False, "error": "zone_name is required"}), 400

    valid_zones = ['front', 'roof', 'side', 'rear']
    if zone_name.lower() not in valid_zones:
        return jsonify({"success": False, "error": f"Invalid zone. Must be one of: {valid_zones}"}), 400

    pressure_data = data_loader.get_pressure_region_by_id(zone_name)

    context_data = f"""
Pressure before: {pressure_data.get('pressure_before_mean') if pressure_data else 'N/A'}
Pressure after: {pressure_data.get('pressure_after_mean') if pressure_data else 'N/A'}
Pressure change: {pressure_data.get('pressure_change') if pressure_data else 'N/A'}
Overall drag reduction: {data_loader.get_drag_reduction_percent()}%
"""

    prompt = get_zone_explanation_prompt(zone_name, context_data, user_question)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.5
        )

        return jsonify({
            "success": True,
            "zone_name": zone_name,
            "explanation": response.choices[0].message.content,
            "pressure_data": pressure_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": "AI provider request failed. Check server configuration and retry."}), 500


@app.route('/explain_shape', methods=['POST'])
def explain_shape():


    data = request.get_json()
    zone_name = data.get('zone_name')

    if not zone_name:
        return jsonify({"success": False, "error": "zone_name is required"}), 400

    valid_zones = ['front', 'roof', 'side', 'rear']
    if zone_name.lower() not in valid_zones:
        return jsonify({"success": False, "error": f"Invalid zone. Must be one of: {valid_zones}"}), 400


    displacement_data = data_loader.get_shape_region_by_id(zone_name)

    if not displacement_data:
        return jsonify({"success": False, "error": f"No shape data found for {zone_name}"}), 404


    all_regions_data = data_loader.get_shape_regions()


    prompt = get_shape_explanation_prompt(zone_name, displacement_data, all_regions_data)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )

        return jsonify({
            "success": True,
            "zone_name": zone_name,
            "explanation": response.choices[0].message.content,
            "data": displacement_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": "AI provider request failed. Check server configuration and retry."}), 500

@app.route('/explain_pressure', methods=['POST'])
def explain_pressure():


    data = request.get_json()
    zone_name = data.get('zone_name')

    if not zone_name:
        return jsonify({"success": False, "error": "zone_name is required"}), 400

    valid_zones = ['front', 'roof', 'side', 'rear']
    if zone_name.lower() not in valid_zones:
        return jsonify({"success": False, "error": f"Invalid zone. Must be one of: {valid_zones}"}), 400


    pressure_data = data_loader.get_pressure_region_by_id(zone_name)

    if not pressure_data:
        return jsonify({"success": False, "error": f"No pressure data found for {zone_name}"}), 404


    prompt = get_pressure_explanation_prompt(zone_name, pressure_data)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )

        return jsonify({
            "success": True,
            "zone_name": zone_name,
            "explanation": response.choices[0].message.content,
            "data": pressure_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": "AI provider request failed. Check server configuration and retry."}), 500


@app.route('/explain_drag', methods=['POST'])
def explain_drag():
    data = request.get_json()
    zone_name = data.get('zone_name')

    if not zone_name:
        return jsonify({"success": False, "error": "zone_name is required"}), 400

    valid_zones = ['front', 'roof', 'side', 'rear']
    if zone_name.lower() not in valid_zones:
        return jsonify({"success": False, "error": f"Invalid zone. Must be one of: {valid_zones}"}), 400


    drag_before = data_loader.get_drag_before()
    drag_after = data_loader.get_drag_after()
    reduction = data_loader.get_drag_reduction_percent()


    pressure_data = data_loader.get_pressure_regions()


    prompt = get_drag_explanation_prompt(zone_name, drag_before, drag_after, reduction, pressure_data)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )

        return jsonify({
            "success": True,
            "zone_name": zone_name,
            "explanation": response.choices[0].message.content,
            "drag": {
                "before": drag_before,
                "after": drag_after,
                "reduction_percent": round(reduction, 2)
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": "AI provider request failed. Check server configuration and retry."}), 500


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question')
    context = data_loader.get_full_context_for_ai()

    if not question:
        return jsonify({"success": False, "error": "No question provided"}), 400


    history = []


    formatted_prompt = get_chat_prompt(question, context)


    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": formatted_prompt}
    ]


    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )

        answer = response.choices[0].message.content


        return jsonify({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        return jsonify({"success": False, "error": "AI provider request failed. Check server configuration and retry."}), 500


@app.route('/clear_history', methods=['POST'])
def clear_history():
    data = request.get_json()
    return jsonify({"success": True, "message": "History cleared"})


@app.route('/region_summary/<region_id>', methods=['GET'])
def get_region_summary(region_id):
    summary = data_loader.get_region_summary(region_id)

    if not summary.get('shape'):
        return jsonify({"success": False, "error": f"Region '{region_id}' not found"}), 404

    return jsonify({
        "success": True,
        "region_id": region_id,
        "shape": summary['shape'],
        "pressure": summary['pressure'],
        "click_coords": summary['click_coords']
    })


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
