from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from google import genai

from files import safe_filename, save_code, is_allowed_file, extract_code_file
from prompts import system_prompt

import os
import uuid
from pathlib import Path


# -------------------------
# APP SETUP
# -------------------------

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated_files"

GENERATED_DIR.mkdir(exist_ok=True)


# -------------------------
# ENVIRONMENT
# -------------------------

load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")


# -------------------------
# GEMINI CLIENT
# -------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# -------------------------
# CONVERSATION MEMORY
# -------------------------

conversations = {}


# -------------------------
# HEALTH CHECK
# -------------------------

@app.route("/", methods=["GET"])
def health_check():

    return jsonify({
        "status": "online",
        "message": "Gemini Code Backend is running"
    })


# -------------------------
# CHAT
# -------------------------

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    message = data.get("message", "").strip()

    session_id = data.get("session_id")

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    # Create session if one doesn't exist
    if not session_id:
        session_id = str(uuid.uuid4())

    # Create conversation
    if session_id not in conversations:
        conversations[session_id] = []

    # Save user's message
    conversations[session_id].append({
        "role": "user",
        "content": message
    })

    # Keep only recent messages
    history = conversations[session_id][-20:]

    # Convert history into a prompt
    prompt = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in history
    )

    try:

        # Send request to Gemini
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "system_instruction": system_prompt
            }
        )

        reply = response.text

    except Exception as error:

        return jsonify({
            "error": "Gemini request failed",
            "details": str(error)
        }), 500

    # Save Gemini response
    conversations[session_id].append({
        "role": "model",
        "content": reply
    })

    # Check if Gemini generated a code file
    file_data = extract_code_file(reply)
    
    files = []
    
    if file_date:
      filename, code = file_date
      
      file_path = save_code(
        filename,
        code,
        GENERATED_DIR
        )
      if file_path:
        files.append({
          "filename": filename,
          "download_url": f"/download/{file_path.name}"
        })

    return jsonify({
        "reply": reply,
        "session_id": session_id,
        "files": files
    })


# -------------------------
# DOWNLOAD GENERATED FILE
# -------------------------

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):

    filename = safe_filename(filename)

    if not is_allowed_file(filename):

        return jsonify({
            "error": "File type not allowed"
        }), 400

    return send_from_directory(
        GENERATED_DIR,
        filename,
        as_attachment=True
    )


# -------------------------
# RUN APP
# -------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )