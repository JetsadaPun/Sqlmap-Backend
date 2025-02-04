from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS  # Import Flask-Cors
import subprocess
import requests
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS ให้กับทุก endpoint

OLLAMA_API_URL = "http://localhost:11434/api/generate"

@app.route('/api/test-url', methods=['POST'])
def test_url():
    data = request.get_json()
    url = data.get('url')
    sqlmap_params = data.get('params', '')  # รับ params จาก request
    
    if not url:
        return jsonify({"result": "", "log": "No URL provided."}), 400

    # Log URL ที่ได้รับมา
    print(f"Received URL: {url}")

    # คำสั่ง SQLMap พร้อม params ที่ส่งมาจาก client
    command = ["sqlmap", "-u", url, "--batch"] + sqlmap_params.split()

    try:
        # รันคำสั่ง sqlmap และจับ output
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # ถ้า sqlmap มี error จะโยน exception
        )
        # ดึง stdout และ stderr
        result = output.stdout
        log = output.stderr
    except subprocess.CalledProcessError as e:
        result = ""
        log = f"An error occurred: {e}"

    # ส่งผลลัพธ์กลับเป็น JSON
    return jsonify({"result": result, "log": log})


DOCUMENTS_FOLDER = os.path.expanduser("~/Documents")
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

def create_pdf(filename, content):
    """ฟังก์ชันสร้างไฟล์ PDF และบันทึกลงในโฟลเดอร์ Documents"""
    pdf_path = os.path.join(DOCUMENTS_FOLDER, filename)

    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica", 12)

    x, y = 50, 800  # ตำแหน่งเริ่มต้น
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


@app.route("/api/receive-data", methods=["POST"])
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

    # ใช้ฟังก์ชัน create_pdf() แทนการสร้างไฟล์ PDF โดยตรง
    pdf_filename = "output.pdf"
    pdf_path = create_pdf(pdf_filename, ai_response)

    return jsonify({
        "message": ai_response,
        "pdfUrl": f"http://localhost:5000/download/{pdf_filename}"
    })

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(DOCUMENTS_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
