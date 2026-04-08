import fitz

def extract_texts_from_pdf(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        texts = [page.get_text() for page in doc]
    return texts