import PyPDF2
import sys

def count_pdf_pages(pdf_file):
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error: {e}")
        return -1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_pdf_pages.py <path_to_pdf>")
        sys.exit(1)

    pdf_file = sys.argv[1]
    pages = count_pdf_pages(pdf_file)
    print(pages)
