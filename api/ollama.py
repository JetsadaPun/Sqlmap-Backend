from flask import Blueprint, request, jsonify, send_from_directory
import requests
from reportlab.pdfgen import canvas
import os

ollama_api = Blueprint("ollama_api", __name__)

DOCUMENTS_FOLDER = os.path.expanduser("~/Documents")
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

def create_pdf(filename, content):
    pdf_path = os.path.join(DOCUMENTS_FOLDER, filename)
    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica", 12)

    x, y = 50, 800
    line_spacing = 20

    for line in content.split("\n"):
        c.drawString(x, y, line)
        y -= line_spacing  
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800

    c.save()
    return pdf_path

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@ollama_api.route("/api/receive-data", methods=["POST"])
def receive_data():
    data = request.get_json()
    user_text = data.get("text", "")

    payload = {
        "model": "deepseek-r1",
        "prompt": user_text,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response_data = response.json()
        ai_response = response_data.get("response", "ไม่ได้รับคำตอบจาก AI")
    except Exception as e:
        ai_response = f"เกิดข้อผิดพลาด: {str(e)}"

    pdf_filename = "output.pdf"
    pdf_path = create_pdf(pdf_filename, ai_response)

    return jsonify({
        "message": ai_response,
        "pdfUrl": f"http://localhost:5000/download/{pdf_filename}"
    })

@ollama_api.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOCUMENTS_FOLDER, filename, as_attachment=True)
