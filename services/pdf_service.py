import fitz

from models.document import Document, PageData, WordData


class PDFService:

    @staticmethod
    def extract(pdf_path):

        document = Document(filename=pdf_path.name, filepath=str(pdf_path))

        with fitz.open(pdf_path) as pdf:

            for page_index, page in enumerate(pdf):

                page_text = page.get_text("text")

                extracted_words = []

                words = page.get_text("words")

                for word in words:

                    extracted_words.append(
                        WordData(
                            text=word[4],
                            x0=word[0],
                            y0=word[1],
                            x1=word[2],
                            y1=word[3],
                            block_no=word[5],
                            line_no=word[6],
                            word_no=word[7],
                        )
                    )

                document.pages.append(
                    PageData(
                        page_number=page_index + 1,
                        text=page_text,
                        words=extracted_words,
                    )
                )

        return document
