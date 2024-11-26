import requests

# Send XHTML content to the new endpoint
response = requests.post(
    "http://127.0.0.1:5000/convert-html",
    headers={"File-Name": "example.xhtml"},
    data="<html><body><h1>XHTML to PDF</h1></body></html>"
)

# Save the returned PDF to a file
with open("output_html.pdf", "wb") as f:
    f.write(response.content)

print("XHTML to PDF conversion successful, saved as output_html.pdf")