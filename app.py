import streamlit as st
import PyPDF2
from pdf2image import convert_from_path
import tempfile
import pytesseract
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="PDF to Text and Image using OCR",
    layout="wide"
)

# Define Poppler path and Tesseract path
POPPLER_PATH = "C:\\Program Files\\poppler-24.08.0\\bin"

# Current Project using OCR Windows 64 bit version 5.5.0.241111
# See: https://github.com/UB-Mannheim/tesseract/wiki 
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

@st.cache_data
def convert_pdf_to_images(pdf_path):
    """
    Convert a PDF file to a list of images, one for each page.

    Parameters:
        pdf_path (str): The file path to the PDF document.

    Returns:
        list: A list of images, each representing a page of the PDF.
    """
    return convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

@st.cache_data
def read_pdf(file):
    """
    Read a PDF file and check for encryption.

    Parameters:
    file (UploadedFile): The uploaded PDF file to be read.

    Returns:
    str: The path to the temporary PDF file.

    Raises:
    ValueError: If the PDF is encrypted and cannot be processed.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file.read())
        temp_pdf_path = temp_pdf.name

    pdf_reader = PyPDF2.PdfReader(temp_pdf_path)
    if pdf_reader.is_encrypted:
        raise ValueError("The PDF is encrypted and cannot be processed.")
    
    return temp_pdf_path

@st.cache_data
def extract_text_from_image(image_bytes):
    """
    Extracts text from an image using OCR.

    Args:
        image_bytes (bytes): The image data in bytes format.

    Returns:
        str: The extracted text from the image.
    """
    image = Image.open(BytesIO(image_bytes))
    return pytesseract.image_to_string(image)

def get_image_download_link(image, filename="page.png"):
    """
    Convert a PIL Image object to bytes and generate a filename for download.

    Args:
        image (PIL.Image.Image): The image to be converted.
        filename (str, optional): The name to assign to the downloadable file. Defaults to "page.png".

    Returns:
        tuple: A tuple containing the image bytes and the filename.
    """
    image_buffer = BytesIO()
    image.save(image_buffer, format="PNG")
    image_bytes = image_buffer.getvalue()
    return image_bytes, filename

def main():
    """
    Main application logic for converting PDF files to text and images using OCR.

    This function sets up the Streamlit interface for users to upload a PDF file,
    view its pages as images, and extract text from the images using OCR. It includes
    pagination controls, image display, text extraction, and download functionality.
    """
    st.title("PDF to Text and Image using OCR")
    st.markdown("## Upload and Preview a PDF")
    
    file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if file is not None:
        try:
            # Read and process the PDF
            pdf_path = read_pdf(file)
            images = convert_pdf_to_images(pdf_path)
            
            total_pages = len(images)
            
            # Pagination control outside columns
            page_number = st.number_input(
                "Select Page Number", min_value=1, max_value=total_pages, value=1
            ) - 1  # Convert to zero-based index

            # Extract selected page's image
            selected_image = images[page_number]
            image_buffer = BytesIO()
            selected_image.save(image_buffer, format="PNG")
            image_bytes = image_buffer.getvalue()

            # Extract selected page's image
            selected_image = images[page_number]
            
            # Convert image to bytes for download
            image_bytes, image_filename = get_image_download_link(
                selected_image, filename=f"page_{page_number + 1}.png"
            )
            
            # OCR text extraction
            extracted_text = extract_text_from_image(image_bytes)
            
            # Layout with two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(selected_image, caption=f"Page {page_number + 1}", use_container_width=True)
                
                # Add a download button
                st.download_button(
                    label=f"Download Page {page_number + 1}",
                    data=image_bytes,
                    file_name=image_filename,
                    mime="image/png",
                )
            
            with col2:
                st.markdown("### Extracted Text")
                st.markdown(f"```{extracted_text}```")
        
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Run the app
if __name__ == "__main__":
    main()
