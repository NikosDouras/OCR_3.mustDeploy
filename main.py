#main.py
from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
from utilities import optimize_image, create_pdf, extract_text_from_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    file_content = file.read()
    content_length = len(file_content)

    try:
        image = Image.open(file)
        width, height = image.size
    except IOError:
        return "Invalid image file"

    file.seek(0)

    # Allow both .jpg and .jpeg file types
    if file and file.filename.lower().endswith(('.jpg', '.jpeg')):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if (content_length > 4 * 1024 * 1024) or width <= 50 or height <= 50 or width >= 4200 or height >= 4200:
            optimized_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"optimized_{filename}")
            optimize_image(filepath, optimized_filepath)
            pdf_path = process_file(optimized_filepath)
        else:
            pdf_path = process_file(filepath)

        return redirect(url_for('thank_you', pdf_path=pdf_path))

    return "Invalid file type"



def process_file(filepath):
    text = extract_text_from_image(filepath)

    # Create PDF from extracted text
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(os.path.basename(filepath))[0]}.pdf")
    create_pdf(text, pdf_path)

    return pdf_path


@app.route('/thankyou')
def thank_you():
    pdf_path = request.args.get('pdf_path', '')
    return render_template('thankyou.html', pdf_path=pdf_path)


@app.route('/download/<path:pdf_path>')
def download_file(pdf_path):
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)