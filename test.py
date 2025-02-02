from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-Cors
import subprocess

app = Flask(__name__)
CORS(app)  # เปิดใช้งาน CORS ให้กับทุก endpoint

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

if __name__ == '__main__':
    app.run(debug=True)
