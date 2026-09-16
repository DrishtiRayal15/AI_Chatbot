import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, Response

from chatbot_engine import ChatbotEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_PATH = os.path.join(BASE_DIR, "intents.json")

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-this-in-production"

bot = ChatbotEngine(INTENTS_PATH)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    response_text, tag, quick_replies = bot.get_response(user_message)

    history = session.get("history", [])
    history.append({"role": "user", "text": user_message})
    history.append({"role": "bot", "text": response_text})
    session["history"] = history[-50:]

    return jsonify({
        "reply": response_text,
        "intent": tag,
        "quick_replies": quick_replies
    })


@app.route("/history", methods=["GET"])
def history():
    return jsonify(session.get("history", []))


@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})


@app.route("/download", methods=["GET"])
def download():
    history = session.get("history", [])
    lines = [f"ChatBuddy Transcript — {datetime.now().strftime('%Y-%m-%d %H:%M')}", "-" * 40]
    for entry in history:
        speaker = "You" if entry["role"] == "user" else "ChatBuddy"
        lines.append(f"{speaker}: {entry['text']}")
    content = "\n".join(lines) if history else "No conversation yet."

    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=chat_transcript.txt"}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
