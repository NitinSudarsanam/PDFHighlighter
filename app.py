import os
import json
from flask import Flask, request, render_template, send_file
import fitz  # PyMuPDF

app = Flask(__name__)

def hex_to_rgb(hex):
  rgb = []
  for i in (0, 2, 4):
    decimal = int(hex[i:i+2], 16)
    rgb.append(decimal)
  
  return tuple(rgb)

def normalize_rgb(r, g, b):
    normalized_r = r / 255.0
    normalized_g = g / 255.0
    normalized_b = b / 255.0
    return normalized_r, normalized_g, normalized_b

def set_colors(r, g, b):
    normalized_r, normalized_g, normalized_b = normalize_rgb(r, g, b)
    return normalized_r, normalized_g, normalized_b


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        search_texts = request.form.getlist("search_text[]")
        highlight_colors_hex = request.form.getlist("highlight_color[]")
        highlight_colors_rgb = request.form.getlist("highlight_color_rgb[]")

        if pdf_file.filename != "" and search_texts and len(search_texts) == len(highlight_colors_hex) :
            pdf_data = pdf_file.read()
            doc = fitz.open(stream=pdf_data, filetype="pdf")

            for idx, search_text in enumerate(search_texts):
                if search_text.strip():
                    page_num = 0  # You need to decide which page to search on
                    page = doc.load_page(page_num)
                    text_instances = page.search_for(search_text, quads=True)
                    highlight_colors_h = highlight_colors_hex[idx]
                    highlight_colors_h = highlight_colors_h.lstrip('#')
                    highlight_color_rgb = hex_to_rgb(highlight_colors_h)
                    normalized_r, normalized_g, normalized_b = set_colors(*highlight_color_rgb)

                    print("Search highlight_color_rgb:", highlight_color_rgb)
                    for inst in text_instances:
                        annot = page.add_highlight_annot(inst)
                        annot.set_colors(stroke=[normalized_r, normalized_g, normalized_b], fill=highlight_color_rgb)
                        annot.update()

            temp_output_path = "temp_output.pdf"
            doc.save(temp_output_path, garbage=2, deflate=True, clean=True)
            doc.close()

            response = send_file(
            temp_output_path,
            as_attachment=True,
            download_name="highlighted_pdf.pdf",
            mimetype="application/pdf",
            )

            #os.remove(temp_output_path)  # Delete the temporary file

            return response
        else:
            print("Received data:")
            print("PDF File:", pdf_file.filename)
            print("Search Texts:", search_texts)
            print("Highlight Colors (Hex):", highlight_colors_hex)
            print("Highlight Colors (RGB):", highlight_colors_rgb)
            return "Please provide a PDF file and ensure all input fields are filled." 


    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
