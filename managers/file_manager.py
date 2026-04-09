import io
import fitz


class FileManager:
    """
    Converts uploaded files to PDF and extracts text content.
    """

    # =================================================================
    # GLOBAL FUNCTIONS
    # =================================================================

    def extract_texts_from_pdf(self, uploaded_file) -> list[str]:
        pdf_stream = self._convert_uploaded_file_to_pdf(uploaded_file)

        with fitz.open(stream=pdf_stream.getvalue(), filetype="pdf") as doc:
            texts = [page.get_text() for page in doc]
        return texts

    # =================================================================
    # LOCAL FUNCTIONS
    # =================================================================

    def _convert_uploaded_file_to_pdf(self, uploaded_file) -> io.BytesIO:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        extension = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""

        if extension == "pdf":
            return io.BytesIO(file_bytes)

        if extension in {"txt", "md"}:
            return self._text_file_to_pdf(file_bytes)
        
        if extension in {"csv", "xls", "xlsx", "ods"}:
            return self._sheet_file_to_pdf(file_bytes, extension)
   
        # For image and other supported document formats, rely on PyMuPDF conversion.
        try:
            with fitz.open(stream=file_bytes, filetype=extension or None) as source_doc:
                pdf_bytes = source_doc.convert_to_pdf()
            return io.BytesIO(pdf_bytes)
        except Exception as exc:
            raise ValueError(
                "File type not supported. Supported formats: PDF, TXT, MD, CSV, XLS, XLSX, ODS."
            ) from exc



    def _sheet_file_to_pdf(self, file_bytes: bytes, extension: str) -> io.BytesIO:
        """
        Converts sheet files to PDF.
        """
        import pandas as pd

        if extension == "csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif extension in {"xls", "xlsx", "ods"}:
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported sheet extension for PDF conversion.")

        # Convert to delimited plain text and reuse text->PDF path.
        sheet_text = df.to_csv(index=False)
        return self._text_file_to_pdf(sheet_text.encode("utf-8"))
    


    def _text_file_to_pdf(self, file_bytes: bytes) -> io.BytesIO:
        """
        Converts text files to PDF.
        """
        text = file_bytes.decode("utf-8", errors="ignore")
        with fitz.open() as pdf_doc:
            page = pdf_doc.new_page()
            y = 36
            max_y = page.rect.height - 36

            for line in text.splitlines() or [""]:
                if y > max_y:
                    page = pdf_doc.new_page()
                    y = 36
                    max_y = page.rect.height - 36
                page.insert_text((36, y), line)
                y += 14

            return io.BytesIO(pdf_doc.write())
