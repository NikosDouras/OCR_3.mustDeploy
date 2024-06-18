#utilities.py
import os, requests
from PIL import Image
from fpdf import FPDF

endpoint = os.getenv('AZURE_ENDPOINT')
subscription_key = os.getenv('AZURE_KEY')
version = "vision/v3.1/ocr"
def optimize_image(input_path, output_path, max_size_mb=4, quality=95, min_dim=50, max_dim=4200):
    with Image.open(input_path) as img:
        width, height = img.size
        scaling_factor = 1

        if width > max_dim or height > max_dim:
            scaling_factor = min(max_dim / width, max_dim / height)

        if width < min_dim or height < min_dim:
            scaling_factor = max(min_dim / width, min_dim / height)

        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img.save(output_path, 'JPEG', quality=quality)

        while os.path.getsize(output_path) > max_size_mb * 1024 * 1024:
            quality -= 5
            if quality < 10:
                break
            img.save(output_path, 'JPEG', quality=quality)


def create_pdf(text, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    text = text.encode('latin1', 'replace').decode('latin1')

    pdf.multi_cell(0, 10, text)
    pdf.output(output_path)

def extract_text_from_image(image_path):
    with open(image_path, 'rb') as image_data:
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/octet-stream'
        }
        params = {
            'language': 'unk',
            'detectOrientation': 'true'
        }
        ocr_url = endpoint + version
        response = requests.post(ocr_url, headers=headers, params=params, data=image_data)
        response.raise_for_status()
        analysis = response.json()

        # Extract the text from the response
        text = []
        for region in analysis['regions']:
            for line in region['lines']:
                line_text = ' '.join([word['text'] for word in line['words']])
                text.append(line_text)
        return '\n'.join(text)

