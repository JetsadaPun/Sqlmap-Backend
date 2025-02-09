from flask import Blueprint, request, jsonify
import subprocess
import re

test_api = Blueprint("test_api", __name__)

TECHNIQUE_PATTERNS = {
    "Boolean-Based Blind SQL Injection": r"Type:\s*boolean-based blind", 
    "Time-Based Blind SQL Injection": r"Type:\s*time-based blind",        
    "Error-Based SQL Injection": r"Type:\s*error-based",                 
    "Union-Based SQL Injection": r"Type:\s*UNION query",                  
    "Stacked Queries SQL Injection": r"Type:\s*stacked queries",          
    "Inline Query SQL Injection": r"Type:\s*inline query",                
}
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

    detected_techniques = []
    for technique, pattern in TECHNIQUE_PATTERNS.items():
        if re.search(pattern, result, re.IGNORECASE):
            detected_techniques.append(technique)
            
    return jsonify({"result": result, "log": log,"techniques": detected_techniques})
