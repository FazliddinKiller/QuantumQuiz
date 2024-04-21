# This script extracts text from documents
# It currently supports .pdf files and .txt files
import PyPDF2
from docx import Document

# Returns text of selected pages
def pdf2text(filename,  pages): # string, int, list 
    text = []
    # Extract start and stop attributes from the slice object
    start = pages.start
    print(start)
    try:
        stop = int(pages.stop)
    except:
        stop = start
    # Iterate over the range defined by the slice
    with open(filename, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(start-1,stop):
            page = pdf_reader.pages[page_num]
            text.append(str(page.extract_text()))

    return text




def docx2text(filename, pages):
    doc = Document(filename)
    text = []

    # Extract start and stop attributes from the slice object
    start = pages.start
    try:
        stop = int(pages.stop)
    except:
        stop = start+1
    print(type(start), type(stop))
    # Iterate over the range defined by the slice
    for page_num, paragraph in enumerate(doc.paragraphs):
        if start <= page_num < stop:
            text.append(paragraph.text)

    return text


def file_type(filename):
    f_type = filename.split('.')[-1]
    return f_type

def doc2text(filename, pages=slice(0,0)):
    filetype = file_type(filename)
    if filetype == 'pdf':
        text = pdf2text(filename, pages)
        return text
    elif filetype == 'docx':
        text = docx2text(filename, pages)
        return text
    else:
        return 'Unsupported file type! '+ str(filetype)
