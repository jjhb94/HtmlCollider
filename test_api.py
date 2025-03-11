import requests

with open("nke-20241130.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Send XHTML content to the new endpoint
# response = requests.post(
#     "http://127.0.0.1:5000/convert-html",
#     headers={"File-Name": "example.xhtml"},
#     data="<html><body><h1>XHTML to PDF</h1></body></html>"
# )

# Send html content to the endpoint
response = requests.post(
    "http://127.0.0.1:5000/convert-html",
    headers={"File-Name": "nke-20241130_c.html"},
    data=html_content
)

# Save the returned PDF to a file
with open("output_html.pdf", "wb") as f:
    f.write(response.content)

print("XHTML to PDF conversion successful, saved as output_html.pdf")