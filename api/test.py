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

VULNERABLE_PARAM_PATTERN = r"Parameter:\s*(\w+)\s*\((GET|POST|COOKIE|HEADER)\)"
PAYLOAD_PATTERN = r"Payload:\s*(.*)"
DBMS_PATTERN = r"back-end DBMS:\s*([^\n]+)"
WEB_TECH_PATTERN = r"web application technology:\s*([^\n]+)"
SERVER_OS_PATTERN = r"web server operating system:\s*([^\n]+)"


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
    except subprocess.CalledProcessError as e:
        result = ""

    # ตรวจจับเทคนิคที่พบ
    detected_techniques = [tech for tech, pattern in TECHNIQUE_PATTERNS.items() if re.search(pattern, result, re.IGNORECASE)]

    # ดึงข้อมูลที่สำคัญจากผลลัพธ์
    vulnerable_param_match = re.search(VULNERABLE_PARAM_PATTERN, result)
    payload_match = re.findall(PAYLOAD_PATTERN, result)
    dbms_match = re.search(DBMS_PATTERN, result)
    web_tech_match = re.search(WEB_TECH_PATTERN, result)
    server_os_match = re.search(SERVER_OS_PATTERN, result)

    # ดึงข้อมูลตารางและคอลัมน์ที่พบ
    db_match = re.search(r"Database:\s+(\w+)", result)
    table_match = re.findall(r"Table:\s+(\w+)", result)
    columns_match = re.findall(r"\| (\w+) \| (\w+)", result)
    

    # เก็บข้อมูลเป็น JSON
    extracted_data = {
        "vulnerable_param": vulnerable_param_match.group(1) if vulnerable_param_match else None,
        "parameter_type": vulnerable_param_match.group(2) if vulnerable_param_match else None,
        "payloads": payload_match if payload_match else None,
        "dbms": dbms_match.group(1) if dbms_match else None,
        "web_technology": web_tech_match.group(1) if web_tech_match else None,
        "server_os": server_os_match.group(1) if server_os_match else None,
        "detected_techniques": detected_techniques,
        "database": db_match.group(1) if db_match else None,
        "table": table_match if table_match else [],
        "columns": [{"name": col[0], "type": col[1]} for col in columns_match] if columns_match else []
    }
    
    print(f"columns: {extracted_data['columns']}")

    return jsonify({"extracted_data": extracted_data})


@test_api.route('/api/technique', methods=['POST'])
def boolean_base():
    data = request.get_json()
    
    # Extract input data
    url = data.get('url')
    techniques = data.get('techniques', '').upper().split(',')
    results = []
    # Build SQLMap command
    for technique in techniques:
        # สร้างคำสั่ง SQLMap
        print('sqlmap', '-u', url, f'--technique={technique}', '--batch')
        mapcommand = ['sqlmap', '-u', url, f'--technique={technique}', '--batch']

        try:
            result = subprocess.run(mapcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout

            # 🔍 ดึงข้อมูลที่ตรงกับ pattern
            vulnerable_param_match = re.search(VULNERABLE_PARAM_PATTERN, output)
            payload_match = re.findall(PAYLOAD_PATTERN, output)
            dbms_match = re.search(DBMS_PATTERN, output)
            web_tech_match = re.search(WEB_TECH_PATTERN, output)
            server_os_match = re.search(SERVER_OS_PATTERN, output)

            results.append({
                "technique": technique,  # บันทึกเทคนิคที่ใช้
                "vulnerable_param": vulnerable_param_match.group(1) if vulnerable_param_match else None,
                "parameter_type": vulnerable_param_match.group(2) if vulnerable_param_match else None,
                "payloads": payload_match if payload_match else None,
                "dbms": dbms_match.group(1) if dbms_match else None,
                "web_technology": web_tech_match.group(1) if web_tech_match else None,
                "server_os": server_os_match.group(1) if server_os_match else None,
            })

        except FileNotFoundError:
            return jsonify({"error": "SQLMap not found. Ensure it is installed"}), 500

    return jsonify({"results": results})  # ส่งข้อมูลกลับเป็น JSON Array
    
@test_api.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()

        required_fields = ['url', 'username', 'email', 'password']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        return jsonify({
            'message': 'Data received successfully',
            'data': {
                'url': data['url'],
                'username': data['username'],
                'email': data['email'],
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@test_api.route('/api/test-crawl', methods=['POST'])
def test_crawl():
    data = request.get_json()
    url = data.get('url')
    sqlmap_params = data.get('params', '')
    if sqlmap_params:
        # หากมีค่า เราจะรวมกับ "--crawl="
        sqlmap_params = "--crawl=" + str(sqlmap_params)

    if not url:
        return jsonify({"result": "", "log": "No URL provided."}), 400

    print(f"Received URL: {url}")
    
    # ใช้ --flush-session เพื่อบังคับ sqlmap วิเคราะห์ใหม่
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

        # Debug: ตรวจสอบค่า stdout
        print(f"Raw stdout output:\n{result}")

        # ใช้ Regular Expression หา URL ที่ถูก Skipped
        skipped_urls = re.findall(r"\[INFO\] skipping '(.*?)'", result)

    except subprocess.CalledProcessError as e:
        result = ""
        log = f"An error occurred: {e}"
        skipped_urls = []

    extracted_data = {
        "skipped_urls": skipped_urls
    }
    
    print(f"Extracted skipped URLs: {extracted_data['skipped_urls']}")  # Debug ตรวจสอบค่าที่ได้

    return jsonify({"extracted_data": extracted_data})