from flask import Blueprint, request, jsonify, send_from_directory
from reportlab.pdfgen import canvas
import json
import os
import re
import uuid
from datetime import datetime
import textwrap

# ตั้งค่า Blueprint
create_pdf = Blueprint("create_pdf_api", __name__)
DOCUMENTS_FOLDER = "Document"
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

def create_sql_injection_report(pdf_filename, title, date, url, techniques, vulnerable_param, parameter_type, payloads, dbms, web_technology, server_os, database, table, columns):
    """สร้าง PDF รายงาน SQL Injection Checklist"""
    pdf_path = os.path.join(DOCUMENTS_FOLDER, pdf_filename)  # ใช้ pdf_filename แทน pdf_filename
    c = canvas.Canvas(pdf_path)

    # ใช้ฟอนต์มาตรฐาน Helvetica
    c.setFont("Helvetica", 16)
    c.drawString(50, 800, title)  # หัวข้อรายงาน
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Date: {date}")

    # วาดเส้นแบ่ง
    c.line(50, 770, 550, 770)
    
    # เขียนชื่อเว็บไซต์
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Website: {url}")  # ชื่อเว็บไซต์

    # เริ่มเขียน Checklist
    y = 725  
    line_spacing = 25
    checkbox_size = 12  
    c.setFont("Helvetica", 14)
    c.drawString(50, y, "SQL Injection Techniques:")
    y -= line_spacing
    
    c.setFont("Helvetica", 12)
    if techniques:
        for technique in techniques:
            checkbox_x = 50
            checkbox_y = y
            c.rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
            c.setFont("Helvetica", 12)
            c.drawString(checkbox_x + 3, checkbox_y + 3, "✓")
            c.drawString(checkbox_x + checkbox_size + 5, y + 3, technique)  
            y -= line_spacing

    
    c.line(50, y, 550, y)
    y -= line_spacing
    # เพิ่มข้อมูล parameter ต่างๆ
    c.setFont("Helvetica", 12)
    y = draw_multiline_text_with_wrap(c, f" • Vulnerable Parameter: {vulnerable_param}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Parameter Type: {parameter_type}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Payloads: {payloads}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • DBMS: {dbms}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Web Technology: {web_technology}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Server OS: {server_os}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Database: {database}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Table: {table}", 50, y, 500)
    y -= 10
    y = draw_multiline_text_with_wrap(c, f" • Columns: {columns}", 50, y, 500)

    if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
    # บันทึก PDF
    c.save()
    return pdf_path


@create_pdf.route("/api/receive-data", methods=["POST"])
def receive_data():
    """รับข้อมูล JSON และสร้าง PDF รายงาน SQL Injection"""
    data = request.get_json()
    print("Received Raw Data:", request.data)  
    print("Parsed JSON Data:", data)  

    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400

    title = "Automated Testing"
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    url = data.get("url", "")
    if not isinstance(url, str) or not url.strip():
        return jsonify({"error": "Invalid or missing URL"}), 400
    
    techniques = data.get("techniques", [])
    if not isinstance(techniques, list):
        return jsonify({"error": "Techniques must be a list"}), 400

    # ✅ ดึง extractedData จาก JSON
    extracted_data = data.get("extractedData", {})
    if not isinstance(extracted_data, dict):
        return jsonify({"error": "Extracted data must be an object"}), 400

    vulnerable_param = extracted_data.get("vulnerable_param", "N/A")
    parameter_type = extracted_data.get("parameter_type", "N/A")
    payloads = extracted_data.get("payloads", "N/A")
    dbms = extracted_data.get("dbms", "N/A")
    web_technology = extracted_data.get("web_technology", "N/A")
    server_os = extracted_data.get("server_os", "N/A")
    database = extracted_data.get("database","N/A")
    table = extracted_data.get("table","N/A")
    columns = extracted_data.get("columns","N/A")

    pdf_filename = f"sql_injection_report_{uuid.uuid4().hex}.pdf"
    pdf_path = create_sql_injection_report(pdf_filename, title, date, url, techniques, vulnerable_param, parameter_type, payloads, dbms, web_technology, server_os, database, table, columns) 

    return jsonify({
        "message": "PDF report created successfully.",
        "pdfUrl": f"http://localhost:5000/download/{pdf_filename}"
    })


@create_pdf.route("/download/<filename>")
def download_file(filename):
    """ให้ดาวน์โหลดไฟล์ PDF อย่างปลอดภัย"""
    if not re.match(r"^[a-zA-Z0-9_\-\.]+\.pdf$", filename):
        return jsonify({"error": "Invalid filename"}), 400

    safe_path = os.path.join(DOCUMENTS_FOLDER, filename)
    
    if not os.path.exists(safe_path) or not safe_path.startswith(DOCUMENTS_FOLDER):
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(DOCUMENTS_FOLDER, filename, as_attachment=True)

def draw_multiline_text_with_wrap(c, text, x, y, max_width, line_spacing=18):
    """ ฟังก์ชันสำหรับวาดข้อความหลายบรรทัด โดยใช้ textwrap เพื่อตัดข้อความให้อยู่ในขนาดที่กำหนด """
    wrapper = textwrap.TextWrapper(width=60)  # กำหนดความยาวที่เหมาะสม
    lines = wrapper.wrap(text)

    # วาดข้อความทีละบรรทัด
    for line in lines:
        c.drawString(x, y, line)
        y -= line_spacing  # ลด y เพื่อเลื่อนไปยังบรรทัดถัดไป

    return y