from flask import Flask, request, send_file;
from xhtml2pdf import pisa;
from io import BytesIO;
import os;

app = Flask(__name__)

@app.route('/convert-html', methods=['POST'])
def convert_to_pdf():
    # grab the HTML content
    html_content = request.data.decode("utf-8");

    # grab HTML filename from header
    original_filename = request.headers.get("File-Name", "document.html");

    # create new PDF filename
    new_filename = os.path.splitext(original_filename)[0] + ".pdf";

    # create a a stream to hold the PDF data
    pdf_stream = BytesIO();

    # convert HTML to PDF using internal converter engine
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_stream);

    if pisa_status.err:
        return "Error converting to PDF", 500;
    
    # go to the beginning of the PDF stream
    pdf_stream.seek(0);

    # send the PDF as a response - 'Content-Disposition

    return send_file(
        pdf_stream, 
        mimetype = 'application/pdf', 
        as_attachment = True,
        download_name = new_filename
    );

"""@app.route('/convert-xhtml', methods=['POST'])
    def convert_xhtml_to_pdf():
        code goes here
"""
# run app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000);