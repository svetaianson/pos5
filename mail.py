import urllib.request
import aiohttp
import io
from docx2pdf import convert

response = urllib.request.urlopen("https://docs.google.com/document/d/18W5XldNpojEXU0gFnKN1p-tczpS20-J8y4hGprHNkao/edit")
async with aiohttp.ClientSession() as session:
    with session.get("https://docs.google.com/document/d/18W5XldNpojEXU0gFnKN1p-tczpS20-J8y4hGprHNkao/edit") as response:
        if response.status == 200:
            content = response.read()
            print(type(content))
            file_like = io.BytesIO(bytes_content)
            doc = docx.Document(file_like)
            print(doc)
            paragraphs = doc.paragraphs