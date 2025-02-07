from flask import Blueprint, request, jsonify
import subprocess

test_api = Blueprint("test_api", __name__)

@test_api.route('/api/test-url', methods=['POST'])
def test_url():
    data = request.get_json()
    url = data.get('url')
    sqlmap_params = data.get('params', '')
    
    if not url:
        return jsonify({"result": "", "log": "No URL provided."}), 400

    print(f"Received URL: {url}")

    command = ["sqlmap", "-u", url, "--batch"] + sqlmap_params.split()

    try:
        output = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  
        )
        result = output.stdout
        log = output.stderr
    except subprocess.CalledProcessError as e:
        result = ""
        log = f"An error occurred: {e}"

    return jsonify({"result": result, "log": log})
