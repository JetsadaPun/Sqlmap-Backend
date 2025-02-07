from flask import Blueprint, request, jsonify, send_from_directory
from reportlab.pdfgen import canvas
import os
import re
import uuid
from werkzeug.utils import safe_join
from datetime import datetime
import textwrap

# ตั้งค่า Blueprint
create_pdf = Blueprint("create_pdf_api", __name__)

# กำหนดโฟลเดอร์เก็บไฟล์ PDF
DOCUMENTS_FOLDER = os.path.expanduser("~/Documents")
if not os.path.exists(DOCUMENTS_FOLDER):
    os.makedirs(DOCUMENTS_FOLDER)

def create_sql_injection_report(filename, title, date, results):
    """สร้าง PDF รายงาน SQL Injection Checklist"""
    pdf_path = os.path.join(DOCUMENTS_FOLDER, filename)
    c = canvas.Canvas(pdf_path)

    # กำหนดชื่อเว็บไซต์เริ่มต้น
    website = "https://www.example.com"

    # ใช้ฟอนต์มาตรฐาน Helvetica
    c.setFont("Helvetica", 16)
    c.drawString(50, 800, title)  # หัวข้อรายงาน
    c.setFont("Helvetica", 12)
    c.drawString(50, 780, f"Date: {date}")

    # วาดเส้นแบ่ง
    c.line(50, 770, 550, 770)
    
    # เขียนชื่อเว็บไซต์
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Website: {website}")  # ชื่อเว็บไซต์

    # เริ่มเขียน Checklist
    y = 725  # ปรับตำแหน่งเริ่มต้นหลังจากเขียนชื่อเว็บไซต์
    line_spacing = 25
    checkbox_size = 12  # ขนาดของ checkbox
    c.setFont("Helvetica", 14)
    c.drawString(50, y, "SQL Injection Techniques:")
    y -= line_spacing
    
    c.setFont("Helvetica", 12)
    for item in results:
        technique = item.get("technique", "Unknown")
        status = item.get("status", "Unknown")
        
        # วาดกล่อง checkbox
        checkbox_x = 50
        checkbox_y = y
        c.rect(checkbox_x, checkbox_y, checkbox_size, checkbox_size)
        if status == "Y":
            c.setFont("Helvetica", 12)
            c.drawString(checkbox_x + 3, checkbox_y + 3, "✓")
        
        # เขียนชื่อเทคนิค
        c.drawString(checkbox_x + checkbox_size + 5, y + 3, technique)  # วางชื่อเทคนิคข้างๆ กล่อง checkbox
        y -= line_spacing

        # เพิ่มคำอธิบาย (Lorem Ipsum)
        lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        c.setFont("Helvetica", 10)
        
        # ความกว้างสูงสุดของข้อความในแต่ละบรรทัด
        max_width = 500  # ความกว้างสูงสุดของข้อความในแต่ละบรรทัด

        # ใช้ textwrap เพื่อแบ่งข้อความ
        wrapped_text = textwrap.wrap(lorem_ipsum, width=50)  # แบ่งข้อความเป็นบรรทัดๆ โดยไม่ให้เกิน 50 ตัวอักษร

        # เขียนข้อความในแต่ละบรรทัด
        for line in wrapped_text:
            c.drawString(checkbox_x + checkbox_size + 5, y + 3, line)
            y -= line_spacing

            # ถ้าหน้ากระดาษเต็ม ให้สร้างหน้าใหม่
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 750

        # ถ้าหน้ากระดาษเต็ม ให้สร้างหน้าใหม่
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

    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400

    title = "Automated Testing"
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ใช้วันเวลาปัจจุบัน
    results = data.get("results")


    if not isinstance(results, list):
        return jsonify({"error": "Results must be a list"}), 400

    for item in results:
        if not isinstance(item, dict) or "technique" not in item or "status" not in item:
            return jsonify({"error": "Each result must have 'technique' and 'status'"}), 400
        if not isinstance(item["technique"], str) or not isinstance(item["status"], str):
            return jsonify({"error": "Technique and status must be strings"}), 400

    pdf_filename = f"sql_injection_report_{uuid.uuid4().hex}.pdf"
    pdf_path = create_sql_injection_report(pdf_filename, title, date, results)

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
