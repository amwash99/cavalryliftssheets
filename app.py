from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
import io
import base64
import re

def decode_signature(sig_data_raw):
    import re
    if not sig_data_raw or not re.match(r"^data:image/.+;base64,", sig_data_raw):
        return None
    try:
        base64_data = sig_data_raw.split(',')[1]
        decoded = base64.b64decode(base64_data)
        if len(decoded) < 100:  # too short to be real image
            return None
        return decoded
    except Exception as e:
        print("⚠️ Failed to decode signature:", e)
        return None

app = Flask(__name__)

# mm to pt conversion
def mm(mm_val):
    return mm_val * 2.83465

# Converts Y mm-from-top into ReportLab's bottom-left origin system
def mm_from_top(mm_y):
    return mm(297 - mm_y)  # 297mm = A4 page height


@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form

    # Decode base64 image signatures
    engineer_sig =   decode_signature(data.get('engineer_signature', ''))
    customer_sig =        decode_signature(data.get('customer_signature', ''))


    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    c.drawString(mm(21.17), mm_from_top(42.86), data.get('customer', ''))
    c.drawString(mm(25.93), mm_from_top(46.57), data.get('site_address', ''))
    c.drawString(mm(142.87), mm_from_top(35.63), data.get('job_no', ''))
    c.drawString(mm(144.45), mm_from_top(43.21), data.get('travel_start', ''))
    c.drawString(mm(144.45), mm_from_top(50.45), data.get('site_arrival', ''))
    c.drawString(mm(144.45), mm_from_top(58.03), data.get('site_depart', ''))
    c.drawString(mm(144.45), mm_from_top(65.61), data.get('travel_finish', ''))
    c.drawString(mm(188.55), mm_from_top(42.86), data.get('date', ''))
    c.drawString(mm(195.08), mm_from_top(50.97), data.get('total_travel', ''))
    c.drawString(mm(194.72), mm_from_top(58.03), data.get('total_onsite', ''))
    c.drawString(mm(21.34), mm_from_top(70.37), data.get('job_type', ''))
    c.drawString(mm(17.81), mm_from_top(75.49), data.get('our_ref', ''))
    c.drawString(mm(27.34), mm_from_top(79.90), data.get('customer_ref', ''))
    c.drawString(mm(14.11), mm_from_top(89.60), data.get('make', ''))
    c.drawString(mm(54.85), mm_from_top(89.60), data.get('model', ''))
    c.drawString(mm(103.71), mm_from_top(89.60), data.get('description', ''))
    c.drawString(mm(144.63), mm_from_top(89.60), data.get('serial', ''))
    c.drawString(mm(184.90), mm_from_top(89.60), data.get('location', ''))
    c.drawString(mm(8.47), mm_from_top(102.83), data.get('work_description', ''))
    c.drawString(mm(8.47), mm_from_top(134.33), data.get('engineer_report', ''))
    c.drawString(mm(8.47), mm_from_top(194.37), data.get('recommendations', ''))
    c.drawString(mm(46.03), mm_from_top(245.88), data.get('autodialler', ''))
    c.drawString(mm(27.16), mm_from_top(251.70), data.get('logcard', ''))
    c.drawString(mm(140.22), mm_from_top(246.76), data.get('lift_in_service', ''))
    c.drawString(mm(36.86), mm_from_top(264.93), data.get('engineer_name', ''))


    # Signatures (placed manually — adjust if needed)
    if customer_sig:
        c.drawImage(ImageReader(io.BytesIO(customer_sig)), mm(140), mm(15), width=100, height=50, mask='auto')

    if engineer_sig:
        c.drawImage(ImageReader(io.BytesIO(engineer_sig)), mm(40), mm(15), width=100, height=50, mask='auto')

    c.save()
    packet.seek(0)

    # Merge with your uploaded template
    template = PdfReader("Blank Service Sheet4.pdf")
    output = PdfWriter()
    overlay = PdfReader(packet)

    page = template.pages[0]
    page.merge_page(overlay.pages[0])
    output.add_page(page)

    output_stream = io.BytesIO()
    output.write(output_stream)
    output_stream.seek(0)

    # Get file name from form or use default
    filename = data.get('pdf_filename', '').strip()
    if not filename:
        filename = "Completed_Service_Sheet"
    if not filename.lower().endswith('.pdf'):
        filename += ".pdf"

    return send_file(output_stream, as_attachment=True,
                     download_name=filename,
                     mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)