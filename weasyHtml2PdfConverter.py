# from flask import Flask, request, send_file
# from weasyprint import HTML
# from io import BytesIO
# import os
# import re

# app = Flask(__name__)

# @app.route('/convert-html', methods=['POST'])
# def convert_to_pdf():
#     html_content = request.data.decode("utf-8")
#     original_filename = request.headers.get("File-Name", "document.html")
#     new_filename = os.path.splitext(original_filename)[0] + ".pdf"
#     pdf_stream = BytesIO()

#     # Get arguments from request (example)
#     size = request.args.get('size', 'letter')
#     orientation = request.args.get('orientation', 'portrait')
#     leftmargin = request.args.get('leftmargin', '0.5in')
#     rightmargin = request.args.get('rightmargin', '0.5in')
#     topmargin = request.args.get('topmargin', '0.5in')
#     bottommargin = request.args.get('bottommargin', '0.5in')

#     style = f"""
# <style>
# @media print {{
#     @page {{
#         size: {size} {orientation};
#         margin-left: {leftmargin};
#         margin-right: {rightmargin};
#         margin-top: {topmargin};
#         margin-bottom: {bottommargin};
#     }}
# }}
# </style>
# """

#     html_content = re.sub(r'<head>', f'<head>{style}', html_content, 0, re.IGNORECASE)

#     try:
#         HTML(string=html_content).write_pdf(pdf_stream)
#         pdf_stream.seek(0)

#         return send_file(
#             pdf_stream,
#             mimetype='application/pdf',
#             as_attachment=True,
#             download_name=new_filename
#         )
#     except Exception as e:
#         return f"Error converting to PDF: {str(e)}", 500

# if __name__ == "__main__":
#     app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, request, send_file
from weasyprint import HTML
from io import BytesIO
import os
from bs4 import BeautifulSoup
import base64
import requests
from urllib.parse import urljoin
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def embed_images(html_content, base_url):
    """Embeds images as data URIs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith('data:'):
            abs_src = urljoin(base_url, src)
            try:
                response = requests.get(abs_src, stream=True)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode('utf-8')
                img['src'] = f'data:{response.headers["Content-Type"]};base64,{image_data}'
            except requests.exceptions.RequestException as e:
                logging.error(f"Error embedding image {abs_src}: {e}")
    return str(soup)

def inline_critical_css(html_content):
    """Inlines critical CSS."""
    soup = BeautifulSoup(html_content, 'html.parser')
    for style in soup.find_all('style'):
        if style.string:
            all_style_text = style.string
            for tag in soup.find_all():
                if tag.has_attr('style'):
                    tag['style'] = all_style_text + tag['style']
            style.decompose()
    return str(soup)

def add_print_styles(html_content):
    """Adds comprehensive print-specific styles."""
    soup = BeautifulSoup(html_content, 'html.parser')
    style_tag = soup.new_tag('style')
    style_tag.string = """
    @media print {
        /* CSS Reset/Normalize */
        html, body, div, span, applet, object, iframe, h1, h2, h3, h4, h5, h6, p, blockquote, pre, a, abbr, acronym, address, big, cite, code, del, dfn, em, img, ins, kbd, q, s, samp, small, strike, strong, sub, sup, tt, var, b, u, i, center, dl, dt, dd, ol, ul, li, fieldset, form, label, legend, table, caption, tbody, tfoot, thead, tr, th, td, article, aside, canvas, details, embed, figure, figcaption, footer, header, hgroup, menu, nav, output, ruby, section, summary, time, mark, audio, video {
            margin: 0;
            padding: 0;
            border: 0;
            font-size: 100%;
            font: inherit;
            vertical-align: baseline;
        }
        /* End CSS Reset */
        @font-face {
            font-family: 'MyCustomFont';
            src: url('data:font/woff2;base64,d09GMgABAAAAAA...PLACE_FONT_DATA_HERE...') format('woff2'); /* Replace with actual font data */
        }
        @page {
            size: letter;
            margin: 0.25in;
        }
        body {
            font-size: 9.5pt; /* Reduced base font size */
            line-height: 1.3;
            color: #000;
            font-family: 'MyCustomFont', sans-serif;
            width: 100%;
            position: static;
            top: 0;
            overflow-x: hidden;
            letter-spacing: -0.01em;
            word-spacing: -0.01em;
            box-sizing: border-box;
            margin-top: 0;
            padding-left: 0;
            padding-right: 0;
            font-size-adjust: 0.5;
            text-rendering: optimizeLegibility;
        }
        h1, h2, h3, h4, h5, h6 {
            font-weight: bold;
            page-break-after: avoid;
        }
        p, li, td, th {
            font-size: 1em; /* Using em units */
            line-height: 1.25;
            margin-bottom: 1px;
            font-variant-numeric: lining-nums proportional-nums;
            font-variant-ligatures: common-ligatures;
            font-kerning: normal;
        }
        table {
            width: 100% !important;
            border-collapse: collapse;
            table-layout: auto;
        }
        th, td {
            padding: 2px !important;
            text-align: left;
            vertical-align: top;
        }
        /* Remove unwanted borders */
        table, th, td {
            border: none;
        }
        .sec-table, .sec-table th, .sec-table td {
            border: 1px solid #ccc;
        }
        .page-break {
            page-break-before: always;
        }
        .no-print {
          display: none;
        }
        img {
            max-width: 99%;
            height: auto;
            vertical-align: top;
        }
        a {
            text-decoration: none;
            color: #000;
        }
        /* Specific adjustments for SEC filings */
        .sec-table td {
            padding: 2px !important;
        }
        .sec-table th {
            font-weight: bold;
        }
        .specific-element {
            margin-bottom: 3px;
        }
        .no-space p {
            margin: 0 !important;
            padding: 0 !important;
        }
        /* Fine-tune font rendering */
        body {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        /* Remove unwanted border-bottom and text-decoration */
        * {
            border-bottom: none !important;
            text-decoration: none !important;
        }
        /* Remove unneeded whitespace */
        html, body {
            overflow-x: hidden;
        }
        /* Prevent page breaks inside elements */
        div, p, table, tr, img, h1, h2, h3, h4, h5, h6, li, section, article, aside, nav, footer, header {
            page-break-inside: avoid;
        }
        /* Add more specific print styles here */
        /* Targeted Padding and Margin Adjustments */
        .specific-padding-element {
            padding: 5px !important;
        }
        .specific-margin-element {
            margin: 10px !important;
        }
        /* Targeted Vertical Alignment Adjustments */
        .specific-vertical-align-element {
            vertical-align: middle !important;
        }
        /*Global Vertical Alignment*/
        td, img {
            vertical-align: top;
        }
        /* Layout Optimization */
        .multi-column {
            column-count: 2;
            column-gap: 20px;
        }
        .inline-block-element {
            display: inline-block;
        }
        /* Advanced CSS Techniques */
        .flex-container {
            display: flex;
            align-items: center;
        }
        /* Page Break and Spacing Adjustments */
        div, section, article {
            page-break-after: auto;
            height: auto;
        }
        /* Specific width control */
        .specific-width{
            width: 100%;
            max-width: 100%;
        }
        /* Overflow control */
        * {
            max-width: 100%;
            overflow-wrap: break-word;
            word-break: break-all;
        }
        img {
            width: fit-content;
        }
        /* Font control */
        body, p, li, td, th {
            font-feature-settings: "kern" 1, "liga" 1, "calt" 1;
        }
        h1{
            font-size: 1.2em;
        }
        h2{
            font-size: 1.1em;
        }
    }
    """
    soup.head.append(style_tag)
    return str(soup)

@app.route('/convert-html', methods=['POST'])
def convert_to_pdf():
    html_content = request.data.decode("utf-8")
    original_filename = request.headers.get("File-Name", "document.html")
    new_filename = os.path.splitext(original_filename)[0] + ".pdf"
    pdf_stream = BytesIO()

    base_url = request.headers.get('Base-Url', 'http://127.0.0.1:5000/')

    # Pre-process HTML
    try:
        html_content = embed_images(html_content, base_url)
        html_content = inline_critical_css(html_content)
        html_content = add_print_styles(html_content)
    except Exception as e:
        logging.error(f"Error processing HTML: {str(e)}")
        return f"Error processing HTML: {str(e)}", 500

    try:
        HTML(string=html_content).write_pdf(pdf_stream)
        pdf_stream.seek(0)

        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=new_filename
        )
    except Exception as e:
        logging
        logging.error(f"Error converting to PDF: {str(e)}")
        return f"Error converting to PDF: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)